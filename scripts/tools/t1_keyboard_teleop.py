#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

msg = """
T1 Keyboard Teleop Active!
---------------------------
Moving around:
   w
a  s  d

space key, k : force stop
CTRL-C to quit
"""

class T1KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('t1_keyboard_teleop')
        # Publish to cmd_vel
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Robot Parameters
        self.max_lin_vel = 1.0  # m/s
        self.max_ang_vel = 1.0  # rad/s
        self.lin_step = 0.1
        self.ang_step = 0.2

        # Current state
        self.target_lin = 0.0
        self.target_ang = 0.0

        # Run loop at 20Hz
        self.timer = self.create_timer(0.05, self.publish_command)
        self.settings = termios.tcgetattr(sys.stdin)
        self.get_logger().info(msg)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.05) # 0.05s timeout
        key = sys.stdin.read(1) if rlist else None
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def publish_command(self):
        key = self.get_key()
        
        # Dead-man switch / Stop
        if key is None:
            pass # Keep current velocity (or you can decay it to 0 here)
        elif key == ' ' or key == 'k':
            self.target_lin = 0.0
            self.target_ang = 0.0
        # Ramping Logic
        elif key == 'w':
            self.target_lin = min(self.target_lin + self.lin_step, self.max_lin_vel)
        elif key == 's':
            self.target_lin = max(self.target_lin - self.lin_step, -self.max_lin_vel)
        elif key == 'a':
            self.target_ang = min(self.target_ang + self.ang_step, self.max_ang_vel)
        elif key == 'd':
            self.target_ang = max(self.target_ang - self.ang_step, -self.max_ang_vel)
        elif key == '\x03': # CTRL-C
            raise KeyboardInterrupt

        twist = Twist()
        twist.linear.x = float(self.target_lin)
        twist.angular.z = float(self.target_ang)
        self.publisher_.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = T1KeyboardTeleop()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Shutting down teleop node...")
    finally:
        # Publish zero velocity before dying
        zero_twist = Twist()
        node.publisher_.publish(zero_twist)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()