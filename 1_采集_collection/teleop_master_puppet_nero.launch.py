import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    agx_arm_ctrl_pkg_dir = get_package_share_directory("agx_arm_ctrl")

    # 左臂 = master (使能但不控制, 人手可拖动)
    left_arm_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(agx_arm_ctrl_pkg_dir, "launch", "start_single_agx_arm_rviz.launch.py")
        ),
        launch_arguments={
            "can_port": "can_left",
            "namespace": "left_arm",
            "arm_type": "nero",
            "auto_enable": "false",
            "control": "false",
            "leader_mode": "true",
            "effector_type": "agx_gripper",
            "tcp_offset": "[0.1755, 0.0, -0.0235, 0.0, 0.0, 0.0]",
            "fast_mode": "true",
            "fw_version": "v183",
            "pub_rate": "30",
            "enable_timeout": "10.0",
        }.items(),
    )

    # 右臂 = puppet (使能 + 控制, 接收中继命令)
    right_arm_driver_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(agx_arm_ctrl_pkg_dir, "launch", "start_single_agx_arm_rviz.launch.py")
        ),
        launch_arguments={
            "can_port": "can_right",
            "namespace": "right_arm",
            "arm_type": "nero",
            "auto_enable": "true",
            "control": "false",
            "leader_mode": "false",
            "effector_type": "agx_gripper",
            "tcp_offset": "[0.1755, 0.0, -0.0235, 0.0, 0.0, 0.0]",
            "fast_mode": "true",
            "fw_version": "v183",
            "pub_rate": "30",
            "enable_timeout": "10.0",
        }.items(),
    )

    # 软件主从中继: 左臂 feedback → 右臂 control
    master_puppet_relay = Node(
        package="oculus_reader",
        executable="master_puppet_relay.py",
        name="master_puppet_relay",
        output="screen",
        parameters=[
            {
                "master_joint_topic": "/left_arm/feedback/joint_states",
                "puppet_control_topic": "/right_arm/control/joint_states",
                "master_gripper_topic": "/left_arm/feedback/gripper_encoder",
                "puppet_gripper_topic": "/right_arm/control/gripper",
                "gripper_max_range": 0.07,
                "lpf_alpha": 0.8,
            }
        ],
    )

    # gripper bridge (for data_tools 采集)
    left_gripper_bridge = Node(
        package="oculus_reader",
        executable="gripper_status_bridge.py",
        name="left_gripper_bridge",
        output="screen",
        parameters=[{"arm": "left_arm"}],
    )
    right_gripper_bridge = Node(
        package="oculus_reader",
        executable="gripper_status_bridge.py",
        name="right_gripper_bridge",
        output="screen",
        parameters=[{"arm": "right_arm"}],
    )

    return LaunchDescription([
        left_arm_driver_launch,
        right_arm_driver_launch,
        master_puppet_relay,
        left_gripper_bridge,
        right_gripper_bridge,
    ])
