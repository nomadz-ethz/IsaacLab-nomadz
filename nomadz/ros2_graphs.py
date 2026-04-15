import omni.graph.core as og


def create_ros2_camera_publish_graph(
    *,
    graph_path: str,
    camera_prim: str,
    image_topic: str,
    camera_info_topic: str,
    frame_id: str,
    camera_type: str = "rgb",
    width: int = 640,
    height: int = 480,
):
    og.Controller.edit(
        {"graph_path": graph_path, "evaluator_name": "execution"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("CreateRenderProduct", "isaacsim.core.nodes.IsaacCreateRenderProduct"),
                ("CameraHelper", "isaacsim.ros2.bridge.ROS2CameraHelper"),
                ("CameraInfoHelper", "isaacsim.ros2.bridge.ROS2CameraInfoHelper"),
            ],
            og.Controller.Keys.SET_VALUES: [
                ("CreateRenderProduct.inputs:cameraPrim", camera_prim),
                ("CreateRenderProduct.inputs:enabled", True),
                ("CreateRenderProduct.inputs:width", width),
                ("CreateRenderProduct.inputs:height", height),
                ("CameraHelper.inputs:topicName", image_topic),
                ("CameraHelper.inputs:type", camera_type),
                ("CameraHelper.inputs:frameId", frame_id),
                ("CameraInfoHelper.inputs:topicName", camera_info_topic),
                ("CameraInfoHelper.inputs:frameId", frame_id),
            ],
            og.Controller.Keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "CreateRenderProduct.inputs:execIn"),
                ("CreateRenderProduct.outputs:execOut", "CameraHelper.inputs:execIn"),
                ("CreateRenderProduct.outputs:execOut", "CameraInfoHelper.inputs:execIn"),
                ("CreateRenderProduct.outputs:renderProductPath", "CameraHelper.inputs:renderProductPath"),
                ("CreateRenderProduct.outputs:renderProductPath", "CameraInfoHelper.inputs:renderProductPath"),
            ],
        },
    )


def setup_booster_k1_realsense_publishers(env_index: int = 0, namespace: str = "/robot1"):
    base = f"/World/envs/env_{env_index}/Robot/head_pitch_link/Realsense/RSD455"

    create_ros2_camera_publish_graph(
        graph_path=f"/World/ROS2_BoosterK1_ColorCamera_{env_index}",
        camera_prim=f"{base}/Camera_OmniVision_OV9782_Color",
        image_topic=f"{namespace}/camera/color/image_raw",
        camera_info_topic=f"{namespace}/camera/color/camera_info",
        frame_id="booster_k1_color_optical_frame",
        camera_type="rgb",
    )

    create_ros2_camera_publish_graph(
        graph_path=f"/World/ROS2_BoosterK1_DepthCamera_{env_index}",
        camera_prim=f"{base}/Camera_Pseudo_Depth",
        image_topic=f"{namespace}/camera/depth/image_raw",
        camera_info_topic=f"{namespace}/camera/depth/camera_info",
        frame_id="booster_k1_depth_optical_frame",
        camera_type="depth",
    )

    create_ros2_camera_publish_graph(
        graph_path=f"/World/ROS2_BoosterK1_LeftCamera_{env_index}",
        camera_prim=f"{base}/Camera_OmniVision_OV9782_Left",
        image_topic=f"{namespace}/camera/left/image_raw",
        camera_info_topic=f"{namespace}/camera/left/camera_info",
        frame_id="booster_k1_left_optical_frame",
        camera_type="rgb",
    )

    create_ros2_camera_publish_graph(
        graph_path=f"/World/ROS2_BoosterK1_RightCamera_{env_index}",
        camera_prim=f"{base}/Camera_OmniVision_OV9782_Right",
        image_topic=f"{namespace}/camera/right/image_raw",
        camera_info_topic=f"{namespace}/camera/right/camera_info",
        frame_id="booster_k1_right_optical_frame",
        camera_type="rgb",
    )


def setup_booster_k1_joint_state_publisher(
    target_prim: str = "/World/envs/env_0/Robot",
    topic_name: str = "/robot1/joint_states",
    graph_path: str = "/World/ROS2_BoosterK1_JointStateGraph",
):
    og.Controller.edit(
        {"graph_path": graph_path, "evaluator_name": "execution"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("OnPlaybackTick", "omni.graph.action.OnPlaybackTick"),
                ("JointStatePub", "isaacsim.ros2.bridge.ROS2PublishJointState"),
            ],
            og.Controller.Keys.SET_VALUES: [
                ("JointStatePub.inputs:targetPrim", target_prim),
                ("JointStatePub.inputs:topicName", topic_name),
            ],
            og.Controller.Keys.CONNECT: [
                ("OnPlaybackTick.outputs:tick", "JointStatePub.inputs:execIn"),
            ],
        },
    )