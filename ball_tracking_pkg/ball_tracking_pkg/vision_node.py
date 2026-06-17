import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import cv2
import numpy as np

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        
        # Subscribe to the camera
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        
        # Publisher to send the ball's position to the control node
        self.publisher_ = self.create_publisher(Point, '/ball_info', 10)
        
        self.bridge = CvBridge()
        self.target_center_x = 320 # Assuming a 640x480 resolution camera
        self.get_logger().info("Vision Node started. Looking for blue ball...")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Image Error: {e}")
            return

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Your custom blue hue values
        lower_blue = np.array([70, 50, 50])
        upper_blue = np.array([100, 255, 255])
        
        mask = cv2.inRange(hsv_frame, lower_blue, upper_blue)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        ball_detected = False
        ball_x = 0
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    ball_x = int(M["m10"] / M["m00"])
                    ball_y = int(M["m01"] / M["m00"])
                    ball_detected = True
                    cv2.circle(frame, (ball_x, ball_y), 10, (0, 255, 0), -1)
                break 
        
        # Create the message to send to the Control Node
        msg_out = Point()
        
        if ball_detected:
            # x stores the error (difference between center and ball)
            msg_out.x = float(self.target_center_x - ball_x)
            msg_out.z = 1.0 # 1.0 means TRUE (Detected)
        else:
            msg_out.x = 0.0
            msg_out.z = 0.0 # 0.0 means FALSE (Not Detected)
            
        # Publish the message
        self.publisher_.publish(msg_out)

        # Show the video feed
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