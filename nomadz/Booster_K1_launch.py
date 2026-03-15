import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    isaaclab_path = os.environ.get('ISAACLAB_PATH', os.path.expanduser("~/IsaacLab"))
    nodes_dir = FindPackageShare("nodes")
    
    robot_namespace = LaunchConfiguration("robot_namespace")
    task_name = LaunchConfiguration("task")
    
    isaaclab_sim = ExecuteProcess(
        cmd=[
            PathJoinSubstitution([isaaclab_path, "isaaclab.sh"]),
            "-p", "scripts/reinforcement_learning/rsl_rl/train.py",
            "--task", task_name,
            "--num_envs", "1" 
        ],
        cwd=isaaclab_path,
        output='screen',
        shell=True
    )

    robot_nodes = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([nodes_dir, "sim_robot_nodes_launch.py"])
        ),
        launch_arguments={
            "robot_namespace": robot_namespace,
        }.items(),
    )

    namespaced_group = GroupAction([
        PushRosNamespace(robot_namespace),
        robot_nodes
    ])

    return LaunchDescription([
        # Arguments
        DeclareLaunchArgument(
            "robot_namespace",
            default_value="robot1",
            description="Namespace for the robot nodes"
        ),
        DeclareLaunchArgument(
            "task",
            default_value="Isaac-Booster-K1.v0",
            description="The Isaac Lab task environment"
        ),
        
        # Actions
        isaaclab_sim,
        namespaced_group
    ])