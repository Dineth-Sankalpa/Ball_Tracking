from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ball_tracking_pkg',
            executable='vision_node',
            name='vision_node',
            output='screen'
        ),
        Node(
            package='ball_tracking_pkg',
            executable='control_node',
            name='control_node',
            output='screen'
        )
    ])