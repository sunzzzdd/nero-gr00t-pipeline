#!/usr/bin/env python3
"""
将 agx_arm 的 GripperStatus 消息转换为 data_msgs::Gripper
data_tools 采集需要 data_msgs/Gripper (angle + distance)
"""

import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
import os

# 延迟加载：data_msgs 可能在另一 workspace，启动时检查
try:
    from data_msgs.msg import Gripper
except ImportError:
    Gripper = None

from agx_arm_msgs.msg import GripperStatus


class GripperBridgeNode(Node):
    def __init__(self):
        super().__init__("gripper_status_bridge")

        self.declare_parameter("arm", "left_arm")
        self.declare_parameter("gripper_max_width", 0.07)  # Nero 夹爪全开 7cm
        self.declare_parameter("input_topic", "")
        self.declare_parameter("output_topic", "")

        arm = str(self.get_parameter("arm").value)
        gripper_max_width = float(self.get_parameter("gripper_max_width").value)

        input_topic = str(self.get_parameter("input_topic").value) or f"/{arm}/feedback/gripper_status"
        output_topic = str(self.get_parameter("output_topic").value) or f"/{arm}/feedback/gripper_encoder"

        self.gripper_max_width = gripper_max_width
        self._last_distance = 0.0

        if Gripper is None:
            self.get_logger().error(
                "data_msgs.msg.Gripper import failed. "
                "Make sure 'data_ws/install/setup.bash' is sourced."
            )

        self.sub = self.create_subscription(
            GripperStatus, input_topic, self._cb, 10
        )
        self.pub = self.create_publisher(Gripper, output_topic, 10) \
            if Gripper is not None else None

        self.get_logger().info(
            f"[{arm}] gripper bridge: {input_topic} (GripperStatus) -> "
            f"{output_topic} (data_msgs/Gripper), max_width={gripper_max_width}m"
        )

    def _cb(self, msg: GripperStatus):
        if Gripper is None or self.pub is None:
            return
        distance = float(msg.width)
        if distance <= 0.0 or distance > self.gripper_max_width * 1.5:
            distance = self._last_distance
        else:
            self._last_distance = distance
        angle = distance / max(self.gripper_max_width, 1e-6)

        out = Gripper()
        out.header = msg.header
        out.angle = angle
        out.distance = distance
        self.pub.publish(out)


def main():
    rclpy.init()
    node = GripperBridgeNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
