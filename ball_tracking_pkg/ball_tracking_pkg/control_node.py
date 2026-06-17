import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point

# Attempt to load the Kobuki library your instructor mentioned
try:
    # Note: Ensure this is the correct import for the specific library you install!
    from kobukidriver import Kobuki
    HAS_KOBUKI = True
except ImportError:
    HAS_KOBUKI = False

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        
        # Subscribe to the data published by the Vision Node
        self.subscription = self.create_subscription(
            Point,
            '/ball_info',
            self.listener_callback,
            10)
        
        self.kp = 0.005 # Tuning constant for rotation speed
        
        if HAS_KOBUKI:
            self.kobuki_robot = Kobuki()
            self.get_logger().info("Connected to Kobuki robot via USB.")
        else:
            self.get_logger().warn("Kobuki library not found. Running in simulation/print mode.")

    def listener_callback(self, msg):
        is_detected = (msg.z == 1.0)
        error_x = msg.x
        
        if is_detected:
            angular_z = self.kp * error_x
            linear_x = 0.1 # Move forward slightly
            self.get_logger().info(f"MOVING - Linear: {linear_x}, Angular: {angular_z:.2f}")
            
            if HAS_KOBUKI:
                # IMPORTANT: Your teammate must verify this exact function name in their library documentation
                # self.kobuki_robot.set_velocity(linear_x, angular_z)
                pass 
                
        else:
            self.get_logger().info("STOPPING - No ball in sight.", throttle_duration_sec=1.5)
            
            if HAS_KOBUKI:
                # self.kobuki_robot.set_velocity(0.0, 0.0)
                pass

def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Send a final stop command when shutting down for safety
        if HAS_KOBUKI:
             # node.kobuki_robot.set_velocity(0.0, 0.0)
             pass
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()