import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point
import math

try:
    from ball_tracking_pkg.QBot import QBot
    HAS_KOBUKI = True
except ImportError as e:
    print(f"Hardware Import Error: {e}")
    HAS_KOBUKI = False

class ControlNode(Node):
    def __init__(self):
        super().__init__('control_node')
        
        self.subscription = self.create_subscription(
            Point,
            '/ball_info',
            self.listener_callback,
            10)
        
        # --- TUNING PARAMETERS ---
        self.kp_angular = 0.005
        self.kp_linear = 0.5    
        self.target_depth = 500.0 # Target distance in mm
        self.depth_tolerance = 40.0 # Deadband: If within 40mm of target, stop moving
        
        # --- VELOCITY SMOOTHING (RAMPING) ---
        self.current_linear_x = 0.0
        self.current_angular_z = 0.0
        self.alpha_v = 0.1 # Acceleration curve: 0.1 = smooth/slow buildup, 0.9 = fast/jerky
        
        self.search_rotations = 0.0  
        self.max_rotations = 2.0     
        
        if HAS_KOBUKI:
            self.kobuki_robot = QBot('/dev/ttyUSB0')
            self.get_logger().info("Connected to Kobuki robot via USB.")
        else:
            self.get_logger().warn("Kobuki library not found. Running in simulation/print mode.")

    def listener_callback(self, msg):
        state = msg.z
        error_x = msg.x
        depth = msg.y 
        
        target_linear_x = 0.0
        target_angular_z = 0.0

        # STATE 1: Actively Tracking the Ball
        if state == 1.0:
            self.search_rotations = 0.0 
            
            # Calculate Target Rotation
            target_angular_z = self.kp_angular * error_x
            
            # Calculate Target Forward/Backward Movement
            if depth != -1.0:
                depth_error = depth - self.target_depth
                
                # DEADBAND FIX: Don't try to move if we are already close enough
                if abs(depth_error) < self.depth_tolerance:
                    target_linear_x = 0.0
                else:
                    target_linear_x = self.kp_linear * depth_error
                    # Increased max speed from 200 to 350 for faster overall tracking
                    target_linear_x = max(-350.0, min(target_linear_x, 350.0))
            else:
                target_linear_x = 0.0

        # STATE 2: Ball Lost - Searching State
        elif state == 0.0 and error_x != 0.0:
            target_linear_x = 0.0 
            if self.search_rotations < self.max_rotations:
                target_angular_z = math.copysign(0.4, error_x)
                dt = 1.0 / 30.0 
                radians_turned = abs(target_angular_z) * dt
                self.search_rotations += radians_turned / (2 * math.pi)
            else:
                target_angular_z = 0.0

        # STATE 3: Idle - No ball ever seen
        else:
            target_linear_x = 0.0
            target_angular_z = 0.0
            
        # --- APPLY VELOCITY SMOOTHING ---
        # This prevents the violent jerk by gradually ramping the current speed to the target speed
        self.current_linear_x = (self.alpha_v * target_linear_x) + ((1.0 - self.alpha_v) * self.current_linear_x)
        self.current_angular_z = (self.alpha_v * target_angular_z) + ((1.0 - self.alpha_v) * self.current_angular_z)
        
        # Round very small smoothed values down to zero to fully stop
        if abs(self.current_linear_x) < 5.0: self.current_linear_x = 0.0
        if abs(self.current_angular_z) < 0.01: self.current_angular_z = 0.0

        self.get_logger().info(f"TRACKING - Lin: {self.current_linear_x:.0f}, Ang: {self.current_angular_z:.2f}, Depth: {depth:.0f}")

        # Translate to Kobuki hardware protocol
        kobuki_speed = 0
        kobuki_radius = 0
        
        if abs(self.current_angular_z) > 0.05 and abs(self.current_linear_x) < 5.0:
            kobuki_radius = 1 if self.current_angular_z > 0 else -1
            kobuki_speed = int(abs(self.current_angular_z) * 115.0) 
        elif abs(self.current_angular_z) <= 0.05:
            kobuki_radius = 0
            kobuki_speed = int(self.current_linear_x)
        else:
            # Prevent Division by Zero just in case
            kobuki_radius = int(self.current_linear_x / self.current_angular_z) if self.current_angular_z != 0 else 0
            kobuki_speed = int(self.current_linear_x)

        if HAS_KOBUKI:
            self.kobuki_robot.set_velocity(kobuki_speed, kobuki_radius)
            
def main(args=None):
    rclpy.init(args=args)
    node = ControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if HAS_KOBUKI:
             # Ensure ints are passed to prevent type errors on shutdown
             node.kobuki_robot.set_velocity(0, 0)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
