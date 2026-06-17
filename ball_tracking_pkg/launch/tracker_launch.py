from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ball_tracking_pkg',
            executable='tracker',
            name='tracker_node',
            output='screen',
            emulate_tty=True  # Helpful to see logs in the terminal
        )
    ])