import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    robot_namespace = LaunchConfiguration("robot_namespace")
    num_envs = LaunchConfiguration("num_envs")

    isaaclab_path = EnvironmentVariable(
        "ISAACLAB_PATH",
        default_value=os.path.expanduser("~/IsaacLab"),
    )

    bringup_pkg = FindPackageShare("nomadz_bringup")

    isaaclab_sim = ExecuteProcess(
        cmd=[
            PathJoinSubstitution([isaaclab_path, "isaaclab.sh"]),
            "-p",
            "nomadz/Booster_K1_launcher.py",
            "--num_envs",
            num_envs,
            "--robot_namespace",
            robot_namespace,
        ],
        cwd=isaaclab_path,
        output="screen",
    )

    robot_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([bringup_pkg, "launch", "sim_robot_nodes.launch.py"])
        ),
        launch_arguments={
            "robot_namespace": robot_namespace,
        }.items(),
    )

    namespaced_group = GroupAction([
        PushRosNamespace(robot_namespace),
        robot_nodes,
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            "robot_namespace",
            default_value="robot1",
            description="Namespace for the robot nodes",
        ),
        DeclareLaunchArgument(
            "num_envs",
            default_value="1",
            description="Number of robots to simulate",
        ),
        isaaclab_sim,
        namespaced_group,
    ])