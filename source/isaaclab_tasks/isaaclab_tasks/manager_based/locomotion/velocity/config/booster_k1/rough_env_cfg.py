
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils import configclass

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as mdp
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg, RewardsCfg

from isaaclab.envs import ManagerBasedRLEnv
from isaaclab.utils.math import quat_apply, quat_conjugate, quat_rotate_inverse
from isaaclab.assets import Articulation
from isaaclab.sensors import ContactSensor
from isaaclab.managers import SceneEntityCfg

import torch

from isaaclab_assets import BOOSTER_K1_CFG  # isort: skip

def feet_y_distance_penalty(env: ManagerBasedRLEnv) -> torch.Tensor:
    robot = env.scene["robot"]
    # find body indices
    left_idx, _  = robot.find_bodies("left_foot_link")
    right_idx, _ = robot.find_bodies("right_foot_link")

    # world-frame foot positions (x,y,z)
    left_pos  = robot.data.body_pose_w[:, left_idx, :3].squeeze(1)
    right_pos = robot.data.body_pose_w[:, right_idx, :3].squeeze(1)

    root_pos  = robot.data.root_pos_w  # [N,3]
    root_quat = robot.data.root_quat_w  # [N,4], quaternion wxyz

    # relative foot‑root vectors
    vec_l = left_pos  - root_pos
    vec_r = right_pos - root_pos

    # rotate into body frame: conjugate of root_quat
    root_quat_conj = quat_conjugate(root_quat)
    left_body  = quat_apply(root_quat_conj, vec_l)
    right_body = quat_apply(root_quat_conj, vec_r)

    # measure lateral (y) distance and compare to target stance width
    error = torch.abs(left_body[:, 1] - right_body[:, 1] - 0.250)

    base_vel = robot.data.root_vel_w  # linear velocity of base in world frame
    low_lat_vel = torch.abs(base_vel[:, 1]) < 0.1

    return error * low_lat_vel.float()


def body_orientation_l2(env: ManagerBasedRLEnv) -> torch.Tensor:
    robot = env.scene["robot"]
    g_body = robot.data.projected_gravity_b

    return torch.sum(g_body[:, :2] ** 2, dim=1)


def feet_stumble(
    env: ManagerBasedRLEnv,
    sensor_cfg: SceneEntityCfg = SceneEntityCfg("contact_forces", body_names=".*_foot$"),
) -> torch.Tensor:
    sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    forces = sensor.data.net_forces_w[:, sensor_cfg.body_ids]
    horizontal = torch.norm(forces[..., :2], dim=-1)
    vertical = torch.abs(forces[..., 2])
    return torch.any(horizontal > 5.0 * vertical, dim=1).float()


def feet_too_near(env: ManagerBasedRLEnv) -> torch.Tensor:
    robot = env.scene["robot"]
    l_idx, _ = robot.find_bodies("left_foot_link")
    r_idx, _ = robot.find_bodies("right_foot_link")

    lp = robot.data.body_pose_w[:, l_idx, :3].squeeze(1)
    rp = robot.data.body_pose_w[:, r_idx, :3].squeeze(1)
    dist = torch.norm(lp - rp, dim=-1)
    return (0.15 - dist).clamp_min(0.0)

@configclass
class K1Rewards(RewardsCfg):
    """Reward terms for Booster K1 (22 DoF) MDP."""

    termination_penalty = RewTerm(func=mdp.is_terminated, weight=-200.0)
    track_lin_vel_xy_exp = RewTerm(
        func=mdp.track_lin_vel_xy_yaw_frame_exp,
        weight=1.0,
        params={"command_name": "base_velocity", "std": 0.5},
    )
    track_ang_vel_z_exp = RewTerm(
        func=mdp.track_ang_vel_z_world_exp, weight=2.0, params={"command_name": "base_velocity", "std": 0.5}
    )
    feet_air_time = RewTerm(
        func=mdp.feet_air_time_positive_biped,
        weight=0.25,
        params={
            "command_name": "base_velocity",
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link"),
            "threshold": 0.4,
        },
    )
    feet_slide = RewTerm(
        func=mdp.feet_slide,
        weight=-0.1,
        params={
            "sensor_cfg": SceneEntityCfg("contact_forces", body_names=".*_foot_link"),
            "asset_cfg": SceneEntityCfg("robot", body_names=".*_foot_link"),
        },
    )

    # === Styling & robustness rewards ===
    feet_y_distance      = RewTerm(func=feet_y_distance_penalty, weight=-2.0)
    torso_upright        = RewTerm(func=body_orientation_l2,       weight=-2.0)
    feet_stumble_penalty = RewTerm(func=feet_stumble,             weight=-2.0)
    feet_too_close       = RewTerm(func=feet_too_near,            weight=-4.0)

    # Penalize ankle joint limits
    dof_pos_limits = RewTerm(
        func=mdp.joint_pos_limits,
        weight=-2.0,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_Ankle_Pitch", ".*_Ankle_Roll"])},
    )
    # Penalize deviation from default of the joints that are not essential for locomotion
    joint_deviation_hip = RewTerm(
        func=mdp.joint_deviation_l1,
        weight=-2,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=[".*_Hip_Yaw", ".*_Hip_Roll"])},
    )
    joint_deviation_arms = RewTerm(
        func=mdp.joint_deviation_l1,
        weight=-1,
        params={
            "asset_cfg": SceneEntityCfg(
                "robot",
                joint_names=[
                    ".*_Shoulder_Pitch",
                    ".*_Shoulder_Roll",
                    ".*_Elbow_Pitch",
                    ".*_Elbow_Yaw",
                ],
            )
        },
    )

    # Small penalty to keep head straight
    joint_deviation_head = RewTerm(
        func=mdp.joint_deviation_l1,
        weight=-1,
        params={"asset_cfg": SceneEntityCfg("robot", joint_names=["AAHead_Yaw", "Head_Pitch"])},
    )


@configclass
class K1RoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    rewards: K1Rewards = K1Rewards()

    def __post_init__(self):
        # post init of parent
        super().__post_init__()
        # Scene
        self.scene.robot = BOOSTER_K1_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.height_scanner.prim_path = "{ENV_REGEX_NS}/Robot/trunk_link"

        # Randomization
        self.events.push_robot = None
        self.events.add_base_mass = None
        self.events.reset_robot_joints.params["position_range"] = (1.0, 1.0)
        self.events.base_external_force_torque.params["asset_cfg"].body_names = ["trunk_link"]
        self.events.reset_base.params = {
            "pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-3.14, 3.14)},
            "velocity_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
        }
        self.events.base_com = None

        # Rewards
        self.rewards.lin_vel_z_l2.weight = 0.0
        self.rewards.undesired_contacts = None
        self.rewards.flat_orientation_l2.weight = -2.0
        self.rewards.action_rate_l2.weight = -0.01
        self.rewards.dof_acc_l2.weight = -2.5e-7
        self.rewards.dof_acc_l2.params["asset_cfg"] = SceneEntityCfg(
            "robot", joint_names=[".*_Hip_.*", ".*_Knee_Pitch"]
        )
        self.rewards.dof_torques_l2.weight = -2.0e-7
        self.rewards.dof_torques_l2.params["asset_cfg"] = SceneEntityCfg(
            "robot", joint_names=[".*_Hip_.*", ".*_Knee_Pitch", ".*_Ankle_.*"]
        )

        # Commands
        self.commands.base_velocity.ranges.lin_vel_x = (0.0, 2.0)
        self.commands.base_velocity.ranges.lin_vel_y = (-0.5, 0.5)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.5, 1.5)

        # terminations
        self.terminations.base_contact.params["sensor_cfg"].body_names = ["trunk_link"]
        self.terminations.low_torso_height = DoneTerm(
        func=mdp.root_height_below_minimum,
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="trunk_link"),
            "minimum_height": 0.30,
        },
    )


@configclass
class K1RoughEnvCfg_PLAY(K1RoughEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # make a smaller scene for play
        self.scene.num_envs = 64
        self.scene.env_spacing = 2.5
        self.episode_length_s = 30.0
        # spawn the robot randomly in the grid (instead of their terrain levels)
        self.scene.terrain.max_init_terrain_level = None
        # reduce the number of terrains to save memory
        if self.scene.terrain.terrain_generator is not None:
            self.scene.terrain.terrain_generator.num_rows = 5
            self.scene.terrain.terrain_generator.num_cols = 5
            self.scene.terrain.terrain_generator.curriculum = False

        self.commands.base_velocity.ranges.lin_vel_x = (1.5, 1.5)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (-1.0, 1.0)
        self.commands.base_velocity.ranges.heading = (0.0, 0.0)
        # disable randomization for play
        self.observations.policy.enable_corruption = False
        # remove random pushing
        self.events.base_external_force_torque = None
        self.events.push_robot = None
