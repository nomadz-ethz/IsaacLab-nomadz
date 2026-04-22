# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""
AMP Humanoid locomotion environment.
"""

import gymnasium as gym

from . import agents

##
# Register Gym environments.
##

gym.register(
    id="Isaac-Humanoid-AMP-Dance-Direct-v0",
    entry_point=f"{__name__}.humanoid_amp_env:HumanoidAmpEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.humanoid_amp_env_cfg:HumanoidAmpDanceEnvCfg",
        "skrl_amp_cfg_entry_point": f"{agents.__name__}:skrl_dance_amp_cfg.yaml",
    },
)

gym.register(
    id="Isaac-Humanoid-AMP-Run-Direct-v0",
    entry_point=f"{__name__}.humanoid_amp_env:HumanoidAmpEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.humanoid_amp_env_cfg:HumanoidAmpRunEnvCfg",
        "skrl_amp_cfg_entry_point": f"{agents.__name__}:skrl_run_amp_cfg.yaml",
    },
)

gym.register(
    id="Isaac-Humanoid-AMP-Walk-Direct-v0",
    entry_point=f"{__name__}.humanoid_amp_env:HumanoidAmpEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.humanoid_amp_env_cfg:HumanoidAmpWalkEnvCfg",
        "skrl_amp_cfg_entry_point": f"{agents.__name__}:skrl_walk_amp_cfg.yaml",
    },
)


gym.register(
    id="Isaac-BoosterK1-AMP-Kick-Direct-v0",
    entry_point=f"{__name__}.booster_amp_env:BoosterK1AmpEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":
            f"{__name__}.booster_amp_env_cfg:BoosterK1AmpEnvCfg",
        "skrl_cfg_entry_point":
            f"{agents.__name__}:skrl_walk_amp_cfg.yaml",
    },
)
# from isaaclab_tasks.utils.hydra import register_task

# register_task(
#     name="Isaac-Humanoid-AMP-Run-Direct-v0",
#     env_cfg_entry_point=f"{__name__}.humanoid_amp_env_cfg:HumanoidAmpRunEnvCfg",
#     agent_cfg_entry_point="skrl:AMP",  # matches your AMP setup
# )

# register_task(
#     name="Isaac-Humanoid-AMP-Dance-Direct-v0",
#     env_cfg_entry_point=f"{__name__}.humanoid_amp_env_cfg:HumanoidAmpDanceEnvCfg",
#     agent_cfg_entry_point="skrl:AMP",
# )
# register_task(
#     name="Isaac-Humanoid-AMP-Walk-Direct-v0",
#     env_cfg_entry_point=f"{__name__}.humanoid_amp_env_cfg:HumanoidAmpWalkEnvCfg",
#     agent_cfg_entry_point="skrl:AMP",
# )
