import threading
from dataclasses import dataclass

from geometry_msgs.msg import Twist
from rclpy.node import Node


@dataclass
class CommandState:
    vx: float = 0.0
    vy: float = 0.0
    wz: float = 0.0


class BoosterK1TeleopBridge(Node):
    def __init__(self, topic_name: str = "/robot1/cmd_vel"):
        super().__init__("booster_k1_teleop_bridge")
        self._lock = threading.Lock()
        self._cmd = CommandState()
        self._sub = self.create_subscription(Twist, topic_name, self._cmd_cb, 10)
        self.get_logger().info(f"Listening for teleop Twist on: {topic_name}")

    def _cmd_cb(self, msg: Twist):
        with self._lock:
            self._cmd.vx = float(msg.linear.x)
            self._cmd.vy = float(msg.linear.y)
            self._cmd.wz = float(msg.angular.z)

    def get_command(self) -> CommandState:
        with self._lock:
            return CommandState(self._cmd.vx, self._cmd.vy, self._cmd.wz)