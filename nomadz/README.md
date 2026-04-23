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


Docker

isaac-lab-base

Run the following command before starting simualtion

export ROS_DISTRO=humble
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=42
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/isaac-sim/exts/isaacsim.ros2.bridge/humble/lib


isaac-lab-ros2

Run the following command before running any ros2 nodes

source /opt/ros/humble/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_DOMAIN_ID=42

To be able to see correct massages, ros2 container needs:

mkdir -p /root/.ros

cat >/root/.ros/fastdds.xml <<'EOF'
<?xml version="1.0" encoding="UTF-8" ?>
<profiles xmlns="http://www.eprosima.com/XMLSchemas/fastRTPS_Profiles">
  <transport_descriptors>
    <transport_descriptor>
      <transport_id>UdpTransport</transport_id>
      <type>UDPv4</type>
    </transport_descriptor>
  </transport_descriptors>

  <participant profile_name="udp_transport_profile" is_default_profile="true">
    <rtps>
      <userTransports>
        <transport_id>UdpTransport</transport_id>
      </userTransports>
      <useBuiltinTransports>false</useBuiltinTransports>
    </rtps>
  </participant>
</profiles>
EOF

export FASTRTPS_DEFAULT_PROFILES_FILE=/root/.ros/fastdds.xml

