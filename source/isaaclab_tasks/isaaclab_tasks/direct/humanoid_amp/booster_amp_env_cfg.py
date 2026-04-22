from isaaclab_assets import BOOSTER_K1_CFG
from isaaclab_tasks.direct.humanoid_amp.humanoid_amp_env_cfg import HumanoidAmpEnvCfg
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.utils.configclass import configclass, field
import os

MOTIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "motions")

@configclass
class BoosterK1AmpEnvCfg(HumanoidAmpEnvCfg):

    motion_file: str = field(default=os.path.join(MOTIONS_DIR, "motion_fixed3.npz"))


    # key_body_names = [
    #     "right_hand_link",
    #     "left_hand_link",
    #     "right_foot_link",
    #     "left_foot_link"
    # ]

    key_body_names = [
        "Left_Shank",
        "Right_Shank",
        "left_foot_link",
        "right_foot_link",
    ]
    reference_body = "trunk_link"
    # Use a global prim path with regex for envs
    robot = BOOSTER_K1_CFG.replace(
        prim_path="/World/envs/env_.*/BoosterK1"
    )
    # Keep original actuators for now; switch to torque later if needed.
    # If you do need torque control across all joints, uncomment below and adjust limits.
    # robot = robot.replace(
    #     actuators={
    #         "body": ImplicitActuatorCfg(
    #             joint_names_expr=[".*"],
    #             stiffness=None,
    #             damping=None,
    #             effort_limit_sim={".*": 120.0},
    #             velocity_limit_sim={".*": 100.0},
    #             armature=0.01,
    #         )
    #     }
    # )