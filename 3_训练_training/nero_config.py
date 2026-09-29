from gr00t.configs.data.embodiment_configs import register_modality_config
from gr00t.data.embodiment_tags import EmbodimentTag
from gr00t.data.types import (
    ActionConfig,
    ActionFormat,
    ActionRepresentation,
    ActionType,
    ModalityConfig,
)
# Nero 单臂（右臂）遥操作数据配置 — 适配 GR00T N1.7
#
# modality.json keys:
#   video:   high, right_wrist
#   state:   right_arm (0:7), right_gripper (7:8)
#   action:  right_arm (0:7), right_gripper (7:8)
#   annotation: human.task_description
#
# 动作表示: 机械臂 RELATIVE (增量), 夹爪 ABSOLUTE (绝对) — 和 SO-101/SO-100 一致
#
# 注: master(左臂) → relay → puppet(右臂), action = master关节角, state = puppet关节角
#     RELATIVE 模式下自动计算 action - state 的 delta, 模型输出增量位移
#     delta_indices=range(0,16): 一次预测未来16帧
nero_config = {
    "video": ModalityConfig(
        delta_indices=[0],
        modality_keys=[
            "high",
            "right_wrist",
        ],
    ),
    "state": ModalityConfig(
        delta_indices=[0],
        modality_keys=[
            "right_arm",
            "right_gripper",
        ],
    ),
    "action": ModalityConfig(
        delta_indices=list(range(0, 16)),  # 扩大 horizon: 8→16，每步覆盖动作翻倍
        modality_keys=[
            "right_arm",
            "right_gripper",
        ],
        action_configs=[
            ActionConfig(
                rep=ActionRepresentation.RELATIVE,   # 机械臂: 增量模式 (和 SO-101 一致)
                type=ActionType.NON_EEF,
                format=ActionFormat.DEFAULT,
            ),
            ActionConfig(
                rep=ActionRepresentation.ABSOLUTE,   # 夹爪: 绝对模式 (和 SO-101 一致)
                type=ActionType.NON_EEF,
                format=ActionFormat.DEFAULT,
            ),
        ],
    ),
    "language": ModalityConfig(
        delta_indices=[0],
        modality_keys=["annotation.human.task_description"],
    ),
}
register_modality_config(nero_config, embodiment_tag=EmbodimentTag.NEW_EMBODIMENT)
