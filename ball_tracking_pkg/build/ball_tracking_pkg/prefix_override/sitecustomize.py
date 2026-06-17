import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/netrunner/Documents/BallTracker/src/ball_tracking_pkg/install/ball_tracking_pkg'
