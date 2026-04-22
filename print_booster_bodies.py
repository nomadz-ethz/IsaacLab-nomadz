from isaaclab_assets import BOOSTER_K1_CFG
from isaaclab.assets import Articulation

robot = Articulation(BOOSTER_K1_CFG)
print("\n".join(robot.data.body_names))
