#!/usr/bin/env python3
"""软件主从中继: 读左臂(master)关节角 → 发给右臂(puppet)控制话题

人手拖动左臂 → 左臂编码器读取关节角 → 中继转发 → 右臂跟随运动
关节角度经一阶低通滤波, 抑制主手传感器噪声导致的从臂抖动。
master 和 puppet 都以 30Hz 发布, 确保采集时帧对齐。
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from data_msgs.msg import Gripper
import numpy as np
import time


class MasterPuppetRelay(Node):
    def __init__(self):
        super().__init__("master_puppet_relay")

        self.declare_parameter("master_joint_topic", "/left_arm/feedback/joint_states")
        self.declare_parameter("puppet_control_topic", "/right_arm/control/joint_states")
        self.declare_parameter("master_gripper_topic", "/left_arm/feedback/gripper_encoder")
        self.declare_parameter("puppet_gripper_topic", "/right_arm/control/gripper")
        self.declare_parameter("gripper_max_range", 0.07)
        self.declare_parameter("lpf_alpha", 0.3)

        self.master_joint_topic = self.get_parameter("master_joint_topic").value
        self.puppet_control_topic = self.get_parameter("puppet_control_topic").value
        self.master_gripper_topic = self.get_parameter("master_gripper_topic").value
        self.puppet_gripper_topic = self.get_parameter("puppet_gripper_topic").value
        self.gripper_max_range = self.get_parameter("gripper_max_range").value
        self.lpf_alpha = self.get_parameter("lpf_alpha").value

        self.joint_pub = self.create_publisher(JointState, self.puppet_control_topic, 10)
        self.gripper_pub = self.create_publisher(Gripper, self.puppet_gripper_topic, 10)

        self.joint_sub = self.create_subscription(
            JointState, self.master_joint_topic, self.joint_callback, 10
        )
        self.gripper_sub = self.create_subscription(
            Gripper, self.master_gripper_topic, self.gripper_callback, 10
        )

        self.prev_joint = None       # 低通滤波历史
        self.last_sent = None        # 上次发送给右臂的位置（用于限速防突变）
        self.max_step = 0.15         # 每帧最大变化量(rad)，~8.6°，防止突变
        self._cb_count = 0           # 调试: 收到消息计数

        self.get_logger().info("软件主从中继启动:")
        self.get_logger().info(f"  master 关节: {self.master_joint_topic}")
        self.get_logger().info(f"  puppet 控制: {self.puppet_control_topic}")
        self.get_logger().info(f"  master 夹爪: {self.master_gripper_topic}")
        self.get_logger().info(f"  puppet 夹爪: {self.puppet_gripper_topic}")
        self.get_logger().info(f"  低通滤波 alpha: {self.lpf_alpha}")
        self.get_logger().info(f"  最大步长: {self.max_step} rad/帧 (防突变)")
        self.get_logger().info(f"  无死区, 无降频, 全速转发")

    def joint_callback(self, msg: JointState):
        self._cb_count += 1
        if self._cb_count % 150 == 1:
            self.get_logger().info(
                f"收到 master 关节 #{self._cb_count}: names={list(msg.name)}, pos={[round(p,3) for p in msg.position]}"
            )

        out = JointState()
        out.header = msg.header
        out.name = msg.name
        out.velocity = msg.velocity
        out.effort = [1.0] * len(msg.position) if msg.position else []

        if not msg.position:
            return

        # 低通滤波
        raw = np.array(msg.position, dtype=float)
        if self.prev_joint is None or len(self.prev_joint) != len(raw):
            self.prev_joint = raw.copy()
        else:
            self.prev_joint = self.lpf_alpha * raw + (1.0 - self.lpf_alpha) * self.prev_joint
        filtered = self.prev_joint.copy()

        # 限速防突变: 每帧每个关节最多变化 max_step rad
        if self.last_sent is None or len(self.last_sent) != len(filtered):
            self.last_sent = filtered.copy()
        else:
            delta = filtered - self.last_sent
            clipped = np.clip(delta, -self.max_step, self.max_step)
            self.last_sent = self.last_sent + clipped

        out.position = self.last_sent.tolist()
        self.joint_pub.publish(out)

    def gripper_callback(self, msg: Gripper):
        out = Gripper()
        out.header = msg.header
        out.distance = float(np.clip(msg.distance, 0.0, self.gripper_max_range))
        out.velocity = msg.velocity
        out.effort = 1.0
        self.gripper_pub.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = MasterPuppetRelay()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
