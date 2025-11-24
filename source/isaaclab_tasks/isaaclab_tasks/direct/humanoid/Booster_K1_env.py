# Copyright (c) 2022-2025, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from isaaclab_assets import BOOSTER_K1_CFG

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, RigidObjectCfg, Articulation
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils import configclass
import torch
import os

from isaaclab_tasks.direct.locomotion.locomotion_env import LocomotionEnv

#* stuff used for debugging. maybe delete later.
# from omni.isaac.core.utils.stage import get_current_stage

# def check_prim_exists(prim_path: str):
#     stage = get_current_stage()
#     prim = stage.GetPrimAtPath(prim_path)
#     if prim.IsValid():
#         print(f"Prim exists at: {prim_path}")
#     else:
#         print(f"Prim NOT found at: {prim_path}")


@configclass
class BoosterK1EnvCfg(DirectRLEnvCfg):
    # env
    episode_length_s = 15.0
    decimation = 2
    action_scale = 1.0
    action_space = 22
    observation_space = 79
    state_space = 0

    # simulation
    sim: SimulationCfg = SimulationCfg(dt=1 / 120, render_interval=decimation)
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="average",
            restitution_combine_mode="average",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    #! using the normal ground for now, but later bring back the field
    # terrain = TerrainImporterCfg(
    #     prim_path="/World/Field",
    #     terrain_type="usd",
    #     usd_path= os.path.expanduser("~/IsaacLab-nomadz/source/isaaclab_assets/data/Field.usd"),
    #     collision_group=-1,
    #     physics_material=sim_utils.RigidBodyMaterialCfg(
    #         friction_combine_mode="average",
    #         restitution_combine_mode="average",
    #         static_friction=1.0,
    #         dynamic_friction=1.0,
    #         restitution=0.0,
    #     ),
    #     debug_vis=False,
    # )

    # scene
    scene: InteractiveSceneCfg = InteractiveSceneCfg(
        num_envs=4096, 
        env_spacing=4.0, 
        replicate_physics=True
    )

    # robot
    robot: ArticulationCfg = BOOSTER_K1_CFG.replace(prim_path="/World/envs/env_.*/Robot")
    
    # # football
    # football: RigidObjectCfg = RigidObjectCfg(
    #     prim_path="/World/envs/env_.*/Football",
    #     spawn=sim_utils.SphereCfg(
    #         radius=0.1,
    #         rigid_props=sim_utils.RigidBodyPropertiesCfg(
    #             rigid_body_enabled=True,
    #             max_linear_velocity=1000.0,
    #             max_angular_velocity=1000.0,
    #             max_depenetration_velocity=100.0,
    #             enable_gyroscopic_forces=True,
    #         ),
    #         mass_props=sim_utils.MassPropertiesCfg(mass=0.45),  # Standard football mass
    #         collision_props=sim_utils.CollisionPropertiesCfg(),
    #         physics_material=sim_utils.RigidBodyMaterialCfg(
    #             static_friction=0.7,
    #             dynamic_friction=0.6,
    #             restitution=0.8,  # Bouncy like a football
    #         ),
    #         visual_material=sim_utils.PreviewSurfaceCfg(
    #             diffuse_color=(1.0, 1.0, 1.0),  # White color
    #             metallic=0.0,
    #         ),
    #     ),
    #     init_state=RigidObjectCfg.InitialStateCfg(
    #         pos=(1.0, 0.0, 0.1),  # 1m in front of robot, at ball radius height
    #         rot=(1.0, 0.0, 0.0, 0.0),  # Identity quaternion
    #     ),
    # )
    
    # TODO Correct these values
    joint_gears: list = [
        50.0,   # AAHead_yaw (head - moderate)
        50.0,   # Head_pitch (head - moderate)
    
        40.0,   # Left_Shoulder_Pitch (arms - lower effort)
        40.0,   # Right_Shoulder_Pitch
    
        40.0,   # Left_Shoulder_Roll
        40.0,   # Right_Shoulder_Roll
    
        40.0,   # Left_Elbow_Pitch
        40.0,   # Right_Elbow_Pitch
    
        40.0,   # Left_Elbow_Yaw
        40.0,   # Right_Elbow_Yaw
    
        
    
        45.0,   # Left_Hip_Pitch (legs - high effort)
        45.0,   # Right_Hip_Pitch
    
        35.0,   # Left_Hip_Roll
        35.0,   # Right_Hip_Roll
    
        35.0,   # Left_Hip_Yaw
        35.0,   # Right_Hip_Yaw
    
        60.0,   # Left_Knee_Pitch (highest effort)
        60.0,   # Right_Knee_Pitch
    
        25.0,   # Left_Ankle_Pitch (feet - moderate)
        25.0,   # Right_Ankle_Pitch
    
        15.0,   # Left_Ankle_Roll (feet - lower effort)
        15.0,   # Right_Ankle_Roll
    ]


    heading_weight: float = 0.5
    up_weight: float = 0.1

    energy_cost_scale: float = 0.05
    actions_cost_scale: float = 0.01
    alive_reward_scale: float = 2.0
    dof_vel_scale: float = 0.1

    death_cost: float = -1.0
    termination_height: float = 0.3  #* arbitrary change for Booster K1

    angular_velocity_scale: float = 0.25
    contact_force_scale: float = 0.01


class BoosterK1Env(LocomotionEnv):
    cfg: BoosterK1EnvCfg

    def __init__(self, cfg: BoosterK1EnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)
        
        #* stuff used for debugging. maybe delete later. 
        # check_prim_exists("/World")
        # check_prim_exists("/World/Field")
        # check_prim_exists("/World/envs")
        # check_prim_exists("/World/envs/env_0/Robot")

    #* this is basically overwriting what's done in LocomotionEnv. Why don't we just create a new env from DirectRLEnv?
    #* even if it's just copy pasting locomotion_env.py entirely it might be worth it for our project since we will eventually change a lot of stuff there
    def _setup_scene(self):  
        """Setup the scene with robot and football."""
        from isaaclab.assets import RigidObject
        
        # Setup robot
        self.robot = Articulation(self.cfg.robot)
        
        # # Setup football
        # self.football = RigidObject(self.cfg.football)
        
        # Add ground plane
        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self.terrain = self.cfg.terrain.class_type(self.cfg.terrain)
        
        # Clone and replicate
        self.scene.clone_environments(copy_from_source=False)
        
        # Filter collisions for CPU simulation
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])
        
        # Add articulation and rigid objects to scene
        self.scene.articulations["robot"] = self.robot
        # self.scene.rigid_objects["football"] = self.football
        
        # Add lights
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)
    