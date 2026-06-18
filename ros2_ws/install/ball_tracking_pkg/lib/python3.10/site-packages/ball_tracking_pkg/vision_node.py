import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np
import math

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
       
        # Subscriptions to the unregistered topics
        self.image_sub = self.create_subscription(
            Image,
            '/image_raw',
            self.image_callback,
            10)
           
        self.depth_sub = self.create_subscription(
            Image,
            '/depth/image_raw',
            self.depth_callback,
            10)
       
        self.publisher_ = self.create_publisher(Point, '/ball_info', 10)
       
        self.bridge = CvBridge()
        self.target_center_x = 320 # Assuming 640x480 resolution
       
        self.latest_depth_frame = None
       
        # --- PARALLAX OFFSET ---
        self.depth_pixel_offset_x = -25
       
        # --- SMOOTHING AND PERSISTENCE STATE ---
        self.last_ball_x = None
        self.last_ball_y = None
        self.alpha = 0.3  # Smoothing factor (0.1 = slow/smooth, 0.9 = fast/reactive)
       
        self.get_logger().info("Vision Node started. Tracking blue ball...")

    def depth_callback(self, msg):
        try:
            self.latest_depth_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except Exception as e:
            self.get_logger().error(f"Depth Error: {e}")

    def get_robust_depth(self, depth_image, center_x, center_y, patch_size=5):
        """Extracts the median depth from a small patch to avoid noise/zeros."""
        half_patch = patch_size // 2
       
        depth_x = center_x + self.depth_pixel_offset_x
        depth_y = center_y
       
        depth_x = max(half_patch, min(depth_x, 639 - half_patch))
        depth_y = max(half_patch, min(depth_y, 479 - half_patch))
       
        patch = depth_image[depth_y-half_patch : depth_y+half_patch+1,
                            depth_x-half_patch : depth_x+half_patch+1]
       
        valid_depths = patch[(patch > 0.0) & (~np.isnan(patch))]
       
        if len(valid_depths) > 0:
            return np.median(valid_depths)
        return -1.0

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            return

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
       
        # --- CALIBRATED COLOR RANGE ---
        lower_blue = np.array([70, 50, 50])
        upper_blue = np.array([100, 255, 255])
       
        mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
       
        ball_detected = False
        curr_x, curr_y = 0, 0
       
        # --- CALIBRATED VISION LOGIC ---
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
           
            if area > 100:
                perimeter = cv2.arcLength(largest_contour, True)
               
                if perimeter > 0:
                    circularity = 4 * np.pi * (area / (perimeter**2))
                   
                    if circularity > 0.25:
                        M = cv2.moments(largest_contour)
                        if M["m00"] != 0:
                            temp_x = int(M["m10"] / M["m00"])
                            temp_y = int(M["m01"] / M["m00"])
                           
                            # --- JERK REJECTION LOGIC ---
                            if self.last_ball_x is not None and abs(temp_x - self.last_ball_x) > 150:
                                ball_detected = False # Ignore this frame, jumped too far
                            else:
                                curr_x, curr_y = temp_x, temp_y
                                ball_detected = True
                               
                                # Draw ball center and depth look-point
                                cv2.circle(frame, (curr_x, curr_y), 10, (0, 255, 0), -1)
                                depth_look_x = max(0, min(curr_x + self.depth_pixel_offset_x, 639))
                                cv2.circle(frame, (depth_look_x, curr_y), 5, (255, 0, 0), -1)
                                cv2.line(frame, (curr_x, curr_y), (depth_look_x, curr_y), (255, 255, 0), 2)

        msg_out = Point()
       
        # --- PUBLISHING LOGIC ---
        if ball_detected:
            # 1. APPLY SMOOTHING (EMA)
            if self.last_ball_x is None:
                self.last_ball_x, self.last_ball_y = float(curr_x), float(curr_y)
            else:
                self.last_ball_x = (self.alpha * curr_x) + ((1 - self.alpha) * self.last_ball_x)
                self.last_ball_y = (self.alpha * curr_y) + ((1 - self.alpha) * self.last_ball_y)
           
            # 2. SET PUBLISHER VALUES
            msg_out.x = float(self.target_center_x - self.last_ball_x)
            msg_out.z = 1.0 # State 1: Actively tracking
           
            # 3. GRAB DEPTH AT SMOOTHED LOCATION
            if self.latest_depth_frame is not None:
                depth_val = self.get_robust_depth(self.latest_depth_frame, int(self.last_ball_x), int(self.last_ball_y))
                msg_out.y = float(depth_val)
               
                status_text = f"Depth: {depth_val:.2f}" if depth_val != -1.0 else "Depth: Invalid"
                color = (0, 255, 0) if depth_val != -1.0 else (0, 0, 255)
                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                msg_out.y = -1.0
               
        elif self.last_ball_x is not None:
            # --- SEARCH MEMORY LOGIC ---
            # Ball is lost, but we remember where it was.
            msg_out.x = float(self.target_center_x - self.last_ball_x)
            msg_out.y = -1.0
            msg_out.z = 0.0 # State 0: Lost/Searching
           
            cv2.putText(frame, "Ball Lost - Searching...", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
           
        else:
            # Startup state: No ball seen yet
            msg_out.x = 0.0
            msg_out.y = 0.0
            msg_out.z = 0.0
            
        self.get_logger().info(f"PUBLISHING -> Error X: {msg_out.x:.1f}px | Depth: {msg_out.y:.1f}mm | State: {msg_out.z}")
        
        self.publisher_.publish(msg_out)

        #cv2.imshow("Vision Processing", frame)
        #cv2.waitKey(1)
           
        self.publisher_.publish(msg_out)

        # Disable graphical output for SSH
        # cv2.imshow("Vision Processing", frame)
        # cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
