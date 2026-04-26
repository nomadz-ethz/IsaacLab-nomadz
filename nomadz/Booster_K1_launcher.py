import argparse

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Run Booster K1 Environment")
parser.add_argument("--num_envs", type=int, default=1, help="Number of robots to simulate.")
parser.add_argument("--robot_namespace", type=str, default="k1", help="ROS namespace for this robot.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

from isaacsim.core.utils.extensions import enable_extension
enable_extension("isaacsim.ros2.bridge")

import torch

from isaaclab_tasks.direct.humanoid.Booster_K1_env import BoosterK1Env, BoosterK1EnvCfg
from nomadz.ros2_graphs import setup_booster_realsense_publishers


def main():
    namespace = f"/{args_cli.robot_namespace.strip('/')}"

    env_cfg = BoosterK1EnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs
    env = BoosterK1Env(cfg=env_cfg)

    setup_booster_realsense_publishers(env_index=0, namespace=namespace, robot_type="k1")
 
    print("[INFO]: Environment setup complete. Starting loop...")

    while simulation_app.is_running():
        with torch.inference_mode():
            actions = torch.zeros((env.num_envs, env.cfg.action_space), device=env.device)
            env.step(actions)

    env.close()
    simulation_app.close()


if __name__ == "__main__":
    main()