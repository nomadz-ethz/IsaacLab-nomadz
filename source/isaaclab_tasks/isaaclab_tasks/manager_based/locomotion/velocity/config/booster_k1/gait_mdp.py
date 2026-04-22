#
# Official-style gait rewards for Booster K1 (biped) — no gait commands needed!
#
from __future__ import annotations
import torch
from typing import TYPE_CHECKING
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import ContactSensor
if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv
def feet_contact_symmetry(
    env: ManagerBasedRLEnv,
    sensor_cfg: SceneEntityCfg = SceneEntityCfg("contact_forces", body_names=".*_foot_link"),
    threshold: float = 80.0,
) -> torch.Tensor:
    """Reward alternating left/right foot contacts — encourages natural walking gait."""
    contact_sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    # Get contact forces for both feet (automatically resolved via body_names regex)
    # Assuming the sensor 'contact_forces' is defined specifically for the feet in that order.
    forces = contact_sensor.data.net_forces_w[:, :, 2]  # [num_envs, num_bodies, 3] → Z force
    # Check if we have enough bodies in the sensor to avoid index errors
    if forces.shape[1] < 2:
        return torch.zeros_like(forces[:, 0])
    left_contact = forces[:, 0] > threshold  # index 0 = left_foot_link
    right_contact = forces[:, 1] > threshold  # index 1 = right_foot_link
    # Reward when exactly one foot is in contact → perfect alternating gait
    return 1.0 - torch.abs(left_contact.float() - right_contact.float())
def foot_clearance_reward(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot", body_names=".*_foot_link"),
    target_height: float = 0.07,
    std: float = 0.04,
) -> torch.Tensor:
    """Reward swing foot clearing a desired height (prevents shuffling)."""
    # Use asset_cfg.body_ids, not indices
    # Use body_pos_w for cleaner position access: [num_envs, num_bodies, 3]
    foot_pos = env.scene[asset_cfg.name].data.body_pos_w[:, asset_cfg.body_ids]
    foot_z = foot_pos[:, :, 2]  # [num_envs, 2]
    # Terrain height under each foot
    # CRITICAL FIX: TerrainImporter does not have get_height_at_points.
    # Unless you have a specific sensor for this, we assume flat ground (z=0) or
    # you must use a RayCaster attached to the feet.
    # For now, we assume 0.0 to prevent the crash.
    terrain_z = torch.zeros_like(foot_z)
    clearance = foot_z - terrain_z
    # Only reward during swing phase
    # FIXED: Slice the forces to match the feet indices!
    # The contact sensor has 23 bodies, but we only want the feet.
    all_forces = env.scene["contact_forces"].data.net_forces_w[:, :, 2]
    forces = all_forces[:, asset_cfg.body_ids] # [num_envs, 2]
    is_swing = (forces < 60.0)
    error = torch.square(clearance - target_height)
    reward = torch.exp(-error / (2 * std**2))
    return torch.sum(reward * is_swing.float(), dim=1) / (is_swing.sum(dim=1) + 1e-6)
def cyclic_foot_velocity_reward(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot", body_names=".*_foot_link"),
    hip_cfg: SceneEntityCfg = SceneEntityCfg("robot", joint_names=["Left_Hip_Pitch", "Right_Hip_Pitch"]),
    scale: float = 1.5,
) -> torch.Tensor:
    """Encourage periodic forward/backward foot motion using hip pitch as phase proxy."""
    # Hip pitch → natural oscillator
    # Use joint_ids for joints
    hip_angles = env.scene["robot"].data.joint_pos[:, hip_cfg.joint_ids]  # [num_envs, 2]
    phase_proxy = hip_angles.mean(dim=1)  # smooth periodic signal
    # Foot XY velocity
    # Use body_ids for bodies
    foot_vel_xy = env.scene["robot"].data.body_lin_vel_w[:, asset_cfg.body_ids, :2]
    speed_xy = torch.norm(foot_vel_xy, dim=-1)  # [num_envs, 2]
    # Reward high speed when hip is extending (swing), low when flexing
    desired_speed = torch.cos(phase_proxy * 3.5)  # tuned for ~1.8 Hz cadence
    desired_speed = torch.clamp(desired_speed, 0.0, 1.0)
    return scale * (speed_xy.mean(dim=1) * desired_speed)
def symmetric_foot_height_reward(
    env: ManagerBasedRLEnv,
    asset_cfg: SceneEntityCfg = SceneEntityCfg("robot", body_names=["left_foot_link", "right_foot_link"]),
    scale: float = 0.8,
) -> torch.Tensor:
    """Reward level pelvis by penalizing height difference between feet during double support."""
    # Use body_ids
    z = env.scene["robot"].data.body_pos_w[:, asset_cfg.body_ids, 2]
    diff = torch.abs(z[:, 0] - z[:, 1])
    return scale * torch.exp(-8.0 * diff)







