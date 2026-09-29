#!/usr/bin/env python3
"""GR00T 推理桥接 — 参考 ALOHA 官方 inference.py 架构
主线程 rclpy.spin() 处理回调, 子线程做推理+200Hz插值执行
依赖: conda activate vt && pip install msgpack msgpack_numpy pyzmq
用法:
  python3 gr00t_inference_client.py --host <IP> --port 5555 \
      --task "..." --control-topic /control/joint_states \
      --feedback-topic /feedback/joint_states
"""
import argparse
import sys
import threading
import time
import numpy as np
import msgpack
import msgpack_numpy as mnp
import zmq
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, JointState
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

# ─── 参数 ────────────────────────────────────────────────────────────────
INTERP_HZ = 200                         # 插值频率 (Hz)
CHUNK_HZ = 30                           # chunk 步频率 (必须和训练数据一致)
ARM_STEPS_LENGTH = 0.01                  # 每个插值步最大关节增量 (rad)
GRIPPER_STEPS_LENGTH = 0.03              # 夹爪每步最大增量
CHUNK_SIZE = 16                          # GR00T 输出 chunk 长度
REINFER_LOOKAHEAD = 10                   # 执行到第10步时开始异步推理
DEFAULT_TASK = "Pick up the red block and place it on the other side"

JOINT_NAMES = ['joint1','joint2','joint3','joint4','joint5','joint6','joint7','gripper']

# ─── ZMQ 序列化 ──────────────────────────────────────────────────────────
def pack(obj):
    return msgpack.packb(obj, default=mnp.encode, use_bin_type=True)

def unpack(data):
    return msgpack.unpackb(data, object_hook=mnp.decode, raw=False)

# ─── 轻量 ZMQ PolicyClient ───────────────────────────────────────────────
class Gr00tClient:
    def __init__(self, host, port, timeout_ms=180000):
        self.host, self.port, self.timeout_ms = host, port, timeout_ms
        self.ctx = zmq.Context()
        self._connect()

    def _connect(self):
        self.sock = self.ctx.socket(zmq.REQ)
        self.sock.setsockopt(zmq.RCVTIMEO, self.timeout_ms)
        self.sock.setsockopt(zmq.SNDTIMEO, self.timeout_ms)
        self.sock.connect(f"tcp://{self.host}:{self.port}")

    def _reset(self):
        try: self.sock.close(linger=0)
        except: pass
        self._connect()

    def ping(self):
        try:
            self.sock.send(pack({"endpoint": "ping"}))
            return unpack(self.sock.recv())
        except:
            self._reset()
            return None

    def get_action(self, obs):
        req = {"endpoint": "get_action", "data": {"observation": obs, "options": None}}
        try:
            self.sock.send(pack(req))
            resp = self.sock.recv()
        except:
            self._reset()
            raise
        result = unpack(resp)
        if isinstance(result, list) and len(result) >= 1:
            return result[0], (result[1] if len(result) > 1 else {})
        if isinstance(result, dict) and "error" in result:
            raise RuntimeError(f"Server error: {result['error']}")
        return result, {}

    def close(self):
        try: self.sock.close(linger=0)
        except: pass
        self.ctx.term()

# ─── 图像工具 ────────────────────────────────────────────────────────────
def yuyv_to_rgb(data, height, width):
    raw = np.frombuffer(data, dtype=np.uint8).reshape(-1, 4)
    y0 = raw[:, 0].astype(np.float32)
    u  = raw[:, 1].astype(np.float32) - 128.0
    y1 = raw[:, 2].astype(np.float32)
    v  = raw[:, 3].astype(np.float32) - 128.0
    r0 = np.clip(y0 + 1.402 * v, 0, 255)
    g0 = np.clip(y0 - 0.344 * u - 0.714 * v, 0, 255)
    b0 = np.clip(y0 + 1.772 * u, 0, 255)
    r1 = np.clip(y1 + 1.402 * v, 0, 255)
    g1 = np.clip(y1 - 0.344 * u - 0.714 * v, 0, 255)
    b1 = np.clip(y1 + 1.772 * u, 0, 255)
    out = np.empty((raw.shape[0] * 2, 3), dtype=np.uint8)
    out[0::2] = np.stack([r0, g0, b0], axis=1)
    out[1::2] = np.stack([r1, g1, b1], axis=1)
    return np.ascontiguousarray(out.reshape(height, width, 3))

def ros_image_to_numpy(msg):
    enc = msg.encoding
    if enc in ("rgb8", "rgba8"):
        c = 4 if enc == "rgba8" else 3
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, c)
        return np.ascontiguousarray(img[:, :, :3])
    if enc == "bgr8":
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)
        return np.ascontiguousarray(img[:, :, ::-1])
    if enc in ("yuyv", "yuyv422", "yuy2", "yuv422_yuy2", "yuv422p"):
        return yuyv_to_rgb(msg.data, msg.height, msg.width)
    if enc == "mono8":
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width)
        return np.ascontiguousarray(np.stack([img] * 3, axis=-1))
    expected_yuyv = msg.height * msg.width * 2
    if len(msg.data) == expected_yuyv:
        return yuyv_to_rgb(msg.data, msg.height, msg.width)
    try:
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)
        if img.shape[2] >= 3:
            return np.ascontiguousarray(img[:, :, :3])
    except:
        pass
    return None

# ─── ROS 2 桥接节点 ──────────────────────────────────────────────────────
class NeroBridge(Node):
    def __init__(self, host, port, task, control_topic, feedback_topic,
                 use_train_video=False, train_video_frames=None, save_cam_dir=None):
        super().__init__("gr00t_nero_bridge")
        self.task = task
        self.running = False

        # 数据存储 — 回调只做赋值, 极轻量
        self._cam_high = None
        self._cam_right = None
        self._joints = None
        self._data_lock = threading.Lock()

        # 训练视频模式
        self.use_train_video = use_train_video
        self.train_video_frames = train_video_frames
        self.train_video_idx = 0

        # 保存相机帧
        self.save_cam_dir = save_cam_dir
        self.save_cam_idx = 0
        if save_cam_dir:
            import os; os.makedirs(save_cam_dir, exist_ok=True)

        # 订阅 — 回调只存数据, 不做任何处理
        if not use_train_video:
            cam_qos = QoSProfile(
                reliability=ReliabilityPolicy.BEST_EFFORT,
                history=HistoryPolicy.KEEP_LAST, depth=1)
            self.create_subscription(Image, "/cam_high/image_raw", self._cb_high, cam_qos)
            self.create_subscription(Image, "/cam_right_wrist/image_raw", self._cb_right, cam_qos)
        self.create_subscription(JointState, feedback_topic, self._cb_joints, 10)
        self.cmd_pub = self.create_publisher(JointState, control_topic, 10)

        # 推理客户端
        self.client = Gr00tClient(host, port)
        self.get_logger().info(f"连接云端 {host}:{port} ...")
        p = self.client.ping()
        if not p:
            self.get_logger().error("❌ Server 连接失败")
            raise SystemExit(1)
        self.get_logger().info(f"✅ Server 连接成功: {p}")

        # 异步推理状态
        self._infer_thread = None
        self._infer_lock = threading.Lock()
        self._infer_actions = None      # (1, chunk, 8) [7 arm + 1 grip]
        self._infer_t_start = None

        # 启动推理线程
        self._ctrl_thread = threading.Thread(target=self._model_loop, daemon=True)
        self._ctrl_thread.start()

    # ── 回调: 只存数据, 极轻量 ─────────────────────────────────────────
    def _cb_high(self, msg):
        img = ros_image_to_numpy(msg)
        if img is not None:
            if self._cam_high is None:
                self.get_logger().info(f"cam_high: {msg.encoding} {msg.width}x{msg.height}")
            self._cam_high = img

    def _cb_right(self, msg):
        img = ros_image_to_numpy(msg)
        if img is not None:
            if self._cam_right is None:
                self.get_logger().info(f"cam_right_wrist: {msg.encoding} {msg.width}x{msg.height}")
            self._cam_right = img

    def _cb_joints(self, msg):
        self._joints = msg

    # ── 获取最新观测 ─────────────────────────────────────────────────────
    def _get_obs(self):
        with self._data_lock:
            if self.use_train_video:
                idx = min(self.train_video_idx, len(self.train_video_frames) - 1)
                cam_high = self.train_video_frames[idx]["cam_high"].copy()
                cam_right = self.train_video_frames[idx]["cam_right"].copy()
                self.train_video_idx += 1
            else:
                cam_high = self._cam_high.copy()
                cam_right = self._cam_right.copy()
            joints = self._joints

        if self.save_cam_dir:
            import cv2
            cv2.imwrite(f"{self.save_cam_dir}/high_{self.save_cam_idx:05d}.jpg",
                        cv2.cvtColor(cam_high, cv2.COLOR_RGB2BGR))
            cv2.imwrite(f"{self.save_cam_dir}/right_{self.save_cam_idx:05d}.jpg",
                        cv2.cvtColor(cam_right, cv2.COLOR_RGB2BGR))
            self.save_cam_idx += 1

        grip_val = joints.position[7] if len(joints.position) > 7 else 0.0
        cam_high = np.ascontiguousarray(cam_high).reshape(1, 1, *cam_high.shape)
        cam_right = np.ascontiguousarray(cam_right).reshape(1, 1, *cam_right.shape)
        right_arm = np.array(joints.position[:7], dtype=np.float32)[np.newaxis, np.newaxis, :]
        right_gripper = np.array([grip_val], dtype=np.float32)[np.newaxis, np.newaxis, :]
        return {
            "video": {"high": cam_high, "right_wrist": cam_right},
            "state": {"right_arm": right_arm, "right_gripper": right_gripper},
            "language": {"annotation.human.task_description": [[self.task]]},
        }, joints

    # ── 异步推理: 在子线程中执行, 不阻塞执行循环 ──────────────────────────
    def _infer_async(self):
        """在子线程中推理, 结果存到 self._infer_actions"""
        try:
            obs, joints = self._get_obs()
            action_chunk, _ = self.client.get_action(obs)
            arm = action_chunk["right_arm"]      # (1, chunk, 7)
            grip = action_chunk["right_gripper"]  # (1, chunk, 1)
            # 合并为 (1, chunk, 8)
            actions = np.concatenate([arm, grip], axis=-1).astype(np.float32)
            with self._infer_lock:
                self._infer_actions = actions
            self.get_logger().info(f"  推理完成: chunk={actions.shape[1]}")
        except Exception as e:
            self.get_logger().error(f"推理异常: {e}")
            with self._infer_lock:
                self._infer_actions = None

    # ── 200Hz 插值执行 ───────────────────────────────────────────────────
    def _publish_interp(self, target_pos, last_pos, dt_chunk):
        """从 last_pos 到 target_pos 做插值, 总时间 = dt_chunk (33ms)"""
        target_pos = np.asarray(target_pos, dtype=np.float32)
        last_pos = np.asarray(last_pos, dtype=np.float32)

        # 按 30Hz 的步间时间算插值步数, 保证总时间≈33ms
        n_steps = max(int(dt_chunk * INTERP_HZ), 1)  # 33ms * 200Hz ≈ 6步
        # 如果位移太大, 增加步数保证每步 ≤ ARM_STEPS_LENGTH
        diff = np.abs(target_pos - last_pos)
        max_arm = diff[:7].max() if len(diff[:7]) > 0 else 0
        step_arm = int(max_arm / ARM_STEPS_LENGTH) if max_arm > 0 else 0
        n_steps = max(n_steps, step_arm, 1)
        if n_steps > 200:
            n_steps = 200

        dt_interp = dt_chunk / n_steps
        traj = np.linspace(last_pos, target_pos, n_steps + 1)
        for i in range(1, len(traj)):
            cmd = JointState()
            cmd.header.stamp = self.get_clock().now().to_msg()
            cmd.name = list(JOINT_NAMES)
            cmd.position = [float(v) for v in traj[i]]
            cmd.position[3] = float(np.clip(cmd.position[3], -2.10, 2.10))
            cmd.position[7] = float(np.clip(cmd.position[7], 0.0, 0.1))
            self.cmd_pub.publish(cmd)
            time.sleep(dt_interp)

        return target_pos

    # ── 主控制循环 (在子线程中运行) ──────────────────────────────────────
    def _model_loop(self):
        # 等数据
        while rclpy.ok():
            with self._data_lock:
                if self.use_train_video:
                    ok = self._joints is not None
                else:
                    ok = self._cam_high is not None and self._cam_right is not None and self._joints is not None
            if ok:
                break
            time.sleep(0.1)

        self.get_logger().info("数据就绪。按 Enter 开始推理控制 ...")
        input()
        self.running = True
        self.get_logger().info("▶ 推理控制开始 (Ctrl+C 停止)")

        rate = self.create_rate(INTERP_HZ)
        dt_interp = 1.0 / INTERP_HZ
        dt_chunk = 1.0 / CHUNK_HZ
        t = 0
        max_t = 0
        all_actions = None
        t_start = 0
        last_pos = None
        first_wait = True

        # 获取初始位置
        with self._data_lock:
            if self._joints is not None:
                last_pos = np.array(self._joints.position[:8], dtype=np.float32)
            else:
                last_pos = np.zeros(8, dtype=np.float32)

        while rclpy.ok() and self.running:
            try:
                # 异步推理: 执行到 lookahead 步时开始下一次推理
                if self._infer_thread is None and (t >= max_t - REINFER_LOOKAHEAD or all_actions is None):
                    self._infer_thread = threading.Thread(target=self._infer_async, daemon=True)
                    self._infer_thread.start()
                    self.get_logger().info(f"  启动异步推理 (t={t}, max_t={max_t})")

                # 检查推理是否完成
                if self._infer_thread is not None and not self._infer_thread.is_alive():
                    self._infer_thread.join()
                    self._infer_thread = None
                    with self._infer_lock:
                        new_actions = self._infer_actions
                        self._infer_actions = None
                    if new_actions is not None:
                        all_actions = new_actions
                        t_start = t
                        max_t = t_start + all_actions.shape[1]
                        self.get_logger().info(f"  切换新chunk: t_start={t_start}, max_t={max_t}")

                # 执行
                if all_actions is None or t >= max_t:
                    if all_actions is None and first_wait:
                        self.get_logger().info("等待首次推理...")
                        first_wait = False
                    time.sleep(dt_chunk)
                    continue

                # 取当前步的目标
                chunk_idx = t - t_start
                if chunk_idx < 0 or chunk_idx >= all_actions.shape[1]:
                    rate.sleep()
                    continue

                target = all_actions[0, chunk_idx]  # (8,)
                if last_pos is None:
                    with self._data_lock:
                        last_pos = np.array(self._joints.position[:8], dtype=np.float32)

                # 200Hz 插值执行
                if chunk_idx == 0:
                    delta = target[:7] - last_pos[:7]
                    self.get_logger().info(
                        f"  t={t} cur={np.round(last_pos[:7],3).tolist()} "
                        f"target={np.round(target[:7],3).tolist()} "
                        f"Δ={np.round(delta,4).tolist()}"
                    )
                last_pos = self._publish_interp(target, last_pos, dt_chunk)
                t += 1

            except KeyboardInterrupt:
                break
            except Exception as e:
                self.get_logger().error(f"执行异常: {e}")
                import traceback; traceback.print_exc()
                time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description="GR00T 推理桥接 (ALOHA架构)")
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=5555)
    parser.add_argument("--task", default=DEFAULT_TASK)
    parser.add_argument("--control-topic", default="/right_arm/control/joint_states")
    parser.add_argument("--feedback-topic", default="/right_arm/feedback/joint_states")
    parser.add_argument("--train-dataset", default=None,
                        help="训练数据集路径 (用训练视频代替相机)")
    parser.add_argument("--train-episode", type=int, default=0)
    parser.add_argument("--save-cam", default=None,
                        help="保存喂给模型的相机帧到此目录")
    parser.add_argument("--cam-dir", default=None,
                        help="用此目录的 jpg 图片代替相机")
    parser.add_argument("--rerun", action="store_true", help="启用 rerun 实时可视化")
    parser.add_argument("--compare-dataset", default=None,
                        help="训练数据集路径 (用于 rerun 对比)")
    parser.add_argument("--compare-episode", type=int, default=0)
    parser.add_argument("--freq", type=int, default=30, help="控制频率 Hz")
    parser.add_argument("--exec-horizon", type=int, default=8, help="每次执行几步 (<=16)")
    args = parser.parse_args()

    # 加载训练视频 (可选)
    train_video_frames = None
    if args.train_dataset:
        import cv2
        from pathlib import Path
        ds_path = Path(args.train_dataset)
        vid_h = ds_path / "videos" / "chunk-000" / "observation.images.cam_high" / f"episode_{args.train_episode:06d}.mp4"
        vid_r = ds_path / "videos" / "chunk-000" / "observation.images.cam_right_wrist" / f"episode_{args.train_episode:06d}.mp4"
        cap_h = cv2.VideoCapture(str(vid_h))
        cap_r = cv2.VideoCapture(str(vid_r))
        train_video_frames = []
        while True:
            ret_h, fh = cap_h.read()
            ret_r, fr = cap_r.read()
            if not ret_h or not ret_r:
                break
            train_video_frames.append({
                "cam_high": cv2.cvtColor(fh, cv2.COLOR_BGR2RGB),
                "cam_right": cv2.cvtColor(fr, cv2.COLOR_BGR2RGB),
            })
        cap_h.release(); cap_r.release()
        print(f"[TRAIN-VIDEO] {len(train_video_frames)} 帧")

    # 从目录加载 jpg 图片代替相机
    if args.cam_dir:
        import cv2
        from pathlib import Path
        cam_path = Path(args.cam_dir)
        files_h = sorted(cam_path.glob("high_*.jpg"))
        files_r = sorted(cam_path.glob("right_*.jpg"))
        train_video_frames = []
        for fh, fr in zip(files_h, files_r):
            train_video_frames.append({
                "cam_high": cv2.cvtColor(cv2.imread(str(fh)), cv2.COLOR_BGR2RGB),
                "cam_right": cv2.cvtColor(cv2.imread(str(fr)), cv2.COLOR_BGR2RGB),
            })
        print(f"[CAM-DIR] 加载 {len(train_video_frames)} 帧来自 {args.cam_dir}")

    # rerun 对比数据
    if args.rerun:
        try:
            import rerun as rr
            rr.init("gr00t_realtime_inference", spawn=True)
            print("[RERUN] 已启用实时可视化")
        except ImportError:
            print("[RERUN] rerun-sdk 未安装, 跳过")

    rclpy.init()
    node = NeroBridge(
        host=args.host, port=args.port, task=args.task,
        control_topic=args.control_topic, feedback_topic=args.feedback_topic,
        use_train_video=train_video_frames is not None,
        train_video_frames=train_video_frames,
        save_cam_dir=args.save_cam,
    )
    try:
        # 主线程 spin — 回调永远不被阻塞
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.running = False
        if node._infer_thread is not None:
            node._infer_thread.join(timeout=1.0)
        node.client.close()
        node.destroy_node()
        try: rclpy.shutdown()
        except: pass

if __name__ == "__main__":
    main()
