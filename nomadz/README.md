Have to set enviroment variables

```
export ISAACLAB_PATH=~/IsaacLab-nomadz
export PYTHONPATH=$PYTHONPATH:~/IsaacLab-nomadz

```

Simulation terminal:

source ~/IsaacLab-nomadz/ros2_ws/install/setup.bash
export ISAACLAB_PATH=~/IsaacLab-nomadz
export PYTHONPATH=$PYTHONPATH:~/IsaacLab-nomadz
ros2 launch nomadz_bringup booster_k1_sim.launch.py

source ~/IsaacLab-nomadz/ros2_ws/install/setup.bash
ros2 run rqt_image_view rqt_image_view