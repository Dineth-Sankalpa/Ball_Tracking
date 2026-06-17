import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
import math

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
        
        self.kp_angular = 0.005 # Tuning constant for tracking rotation speed
        self.kp_linear = 0.5    # Tuning constant for forward/backward speed
        self.target_depth = 0.50 # Target distance in meters
        
        # --- NEW SEARCH TRACKING VARIABLES ---
        self.search_rotations = 0.0  # Tracks how many full circles we've made
        self.max_rotations = 2.0     # Limit to 2 full circles
        
        if HAS_KOBUKI:
            self.kobuki_robot = Kobuki()
            self.get_logger().info("Connected to Kobuki robot via USB.")
        else:
            self.get_logger().warn("Kobuki library not found. Running in simulation/print mode.")

    def listener_callback(self, msg):
        state = msg.z
        error_x = msg.x
        depth = msg.y 
        
        linear_x = 0.0
        angular_z = 0.0

        # STATE 1: Actively Tracking the Ball
        if state == 1.0:
            self.search_rotations = 0.0 # Reset search counter because we found the ball!
            
            # Calculate rotation
            angular_z = self.kp_angular * error_x
            
            # Calculate forward/backward movement
            if depth != -1.0:
                depth_error = depth - self.target_depth
                linear_x = self.kp_linear * depth_error
                # Cap the linear speed so the robot doesn't jerk violently
                linear_x = max(-0.2, min(linear_x, 0.2))
            else:
                # If depth is invalid (NaN), stop moving forward but keep rotating
                linear_x = 0.0 

            self.get_logger().info(f"TRACKING - Lin: {linear_x:.2f}, Ang: {angular_z:.2f}, Depth: {depth:.2f}")

        # STATE 2: Ball Lost - Searching State
        elif state == 0.0 and error_x != 0.0:
            linear_x = 0.0 # Stop forward movement
            
            if self.search_rotations < self.max_rotations:
                # Rotate at a fixed search speed in the direction the ball was last seen
                # math.copysign applies the +/- sign of error_x to the 0.4 speed
                angular_z = math.copysign(0.4, error_x)
                
                # Approximate how much of a circle we just turned
                # (Assuming the vision node runs at ~30 messages per second)
                dt = 1.0 / 30.0 
                radians_turned = abs(angular_z) * dt
                self.search_rotations += radians_turned / (2 * math.pi)
                
                self.get_logger().info(f"SEARCHING - Rotations: {self.search_rotations:.2f}/2.0", throttle_duration_sec=0.5)
            else:
                # Limit reached, stop rotating
                angular_z = 0.0
                self.get_logger().warn("SEARCH FAILED - 2 Rotations completed. Stopping.", throttle_duration_sec=2.0)

        # STATE 3: Idle - No ball ever seen
        else:
            linear_x = 0.0
            angular_z = 0.0
            self.get_logger().info("IDLE - Waiting for ball...", throttle_duration_sec=2.0)
            
        # Send commands to the hardware
        if HAS_KOBUKI:
            # Uncomment the line below when running on the actual robot
            # self.kobuki_robot.set_velocity(linear_x, angular_z)
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
    main()import rclpy
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
        depth = msg.y 
        
        # Target distance (Change to 500.0 if your depth is in millimeters!)
        target_depth = 0.50 
        
        # Linear speed tuning constant
        kp_linear = 0.5  

        if is_detected:
            # 1. Calculate Angular Velocity (Rotation)
            angular_z = self.kp * error_x
            
            # 2. Calculate Linear Velocity (Forward/Backward)
            if depth != -1.0:
                depth_error = depth - target_depth
                linear_x = kp_linear * depth_error
                
                # Cap the speed so the robot doesn't jerk violently
                linear_x = max(-0.2, min(linear_x, 0.2))
            else:
                # If depth is invalid (NaN), stop moving forward but keep rotating to track
                linear_x = 0.0 

            self.get_logger().info(f"MOVING - Linear: {linear_x:.2f}, Angular: {angular_z:.2f}, Depth: {depth:.2f}")
            
            if HAS_KOBUKI:
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
