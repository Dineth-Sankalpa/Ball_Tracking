import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/slam/Desktop/Ball_Tracking/ros2_ws/install/ball_tracking_pkg'
