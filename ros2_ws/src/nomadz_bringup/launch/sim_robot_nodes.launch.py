from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_namespace = LaunchConfiguration("robot_namespace")

    teleop = Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        name="teleop_twist_keyboard",
        output="screen",
        prefix="xterm -e",
        remappings=[
            ("cmd_vel", "cmd_vel"),
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "robot_namespace",
            default_value="robot1",
            description="Namespace for the robot nodes",
        ),
        teleop,
    ])