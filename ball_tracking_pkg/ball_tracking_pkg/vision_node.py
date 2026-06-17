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
            '/camera/color/image_raw',
            self.image_callback,
            10)
            
        self.depth_sub = self.create_subscription(
            Image,
            '/camera/depth/image_raw', 
            self.depth_callback,
            10)
        
        self.publisher_ = self.create_publisher(Point, '/ball_info', 10)
        
        self.bridge = CvBridge()
        self.target_center_x = 320 # Assuming 640x480 resolution
        
        self.latest_depth_frame = None 
        
        # --- PARALLAX OFFSET ---
        # Adjust this value. If the depth is constantly reading the background 
        # instead of the ball, increase or decrease this number.
        self.depth_pixel_offset_x = -25 
        
        self.get_logger().info("Vision Node started. Tracking blue ball...")

    def depth_callback(self, msg):
        try:
            self.latest_depth_frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
        except Exception as e:
            self.get_logger().error(f"Depth Error: {e}")

    def get_robust_depth(self, depth_image, center_x, center_y, patch_size=5):
        """Extracts the median depth from a small patch to avoid noise/zeros."""
        half_patch = patch_size // 2
        
        # Apply the parallax offset to align with the depth camera's perspective
        depth_x = center_x + self.depth_pixel_offset_x
        depth_y = center_y # Vertical offset is usually negligible
        
        # Ensure coordinates are within image bounds (assuming 640x480)
        depth_x = max(half_patch, min(depth_x, 639 - half_patch))
        depth_y = max(half_patch, min(depth_y, 479 - half_patch))
        
        # Extract a small patch of depth values
        patch = depth_image[depth_y-half_patch : depth_y+half_patch+1, 
                            depth_x-half_patch : depth_x+half_patch+1]
        
        # Filter out 0.0 or NaN values (Kinect blind spots)
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
        
        lower_blue = np.array([70, 50, 50])
        upper_blue = np.array([100, 255, 255])
        
        mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ball_detected = False
        ball_x, ball_y = 0, 0
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    ball_x = int(M["m10"] / M["m00"])
                    ball_y = int(M["m01"] / M["m00"])
                    ball_detected = True
                    
                    # Draw ball center
                    cv2.circle(frame, (ball_x, ball_y), 10, (0, 255, 0), -1)
                    
                    # Draw where we are looking for depth
                    depth_look_x = max(0, min(ball_x + self.depth_pixel_offset_x, 639))
                    cv2.circle(frame, (depth_look_x, ball_y), 5, (255, 0, 0), -1)
                    cv2.line(frame, (ball_x, ball_y), (depth_look_x, ball_y), (255, 255, 0), 2)
                break 
        
        msg_out = Point()
        
        if ball_detected:
            msg_out.x = float(self.target_center_x - ball_x)
            msg_out.z = 1.0 
            
            if self.latest_depth_frame is not None:
                depth_val = self.get_robust_depth(self.latest_depth_frame, ball_x, ball_y)
                msg_out.y = float(depth_val)
                
                status_text = f"Depth: {depth_val:.2f}" if depth_val != -1.0 else "Depth: Invalid"
                color = (0, 255, 0) if depth_val != -1.0 else (0, 0, 255)
                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            else:
                msg_out.y = -1.0
        else:
            msg_out.x = 0.0
            msg_out.y = 0.0
            msg_out.z = 0.0
            
        self.publisher_.publish(msg_out)

        cv2.imshow("Vision Processing", frame)
        cv2.waitKey(1)

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