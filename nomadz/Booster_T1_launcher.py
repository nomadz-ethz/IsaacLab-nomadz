import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Run Booster T1 Environment")

parser.add_argument("--num_envs", type=int, default=1, help="Number of robots to simulate.")

AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# 2. Launch the Simulator (Must happen before importing Env/Torch)
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import torch
from isaaclab_tasks.direct.humanoid.Booster_T1_env import BoosterT1Env, BoosterT1EnvCfg

def main():
    env_cfg = BoosterT1EnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs
    env = BoosterT1Env(cfg=env_cfg)

    print(f"[INFO]: Environment setup complete. Starting loop...")

    # 5. Simple Simulation Loop
    while simulation_app.is_running():
        with torch.inference_mode():
            # Example: Zero actions (standing still/gravity test)
            actions = torch.zeros((env.num_envs, env.cfg.action_space), device=env.device)
            
            # Step the physics and observations
            obs, rewards, terminated, truncated, info = env.step(actions)
            
    # Cleanup
    env.close()
    simulation_app.close()

if __name__ == "__main__":
    main()