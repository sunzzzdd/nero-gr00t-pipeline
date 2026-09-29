#!/bin/bash
# ============================================================================
# CAN 多接口配置脚本 (nero3 副本, 不修改官方 can_muti_activate.sh)
#
# 用途: 按本机 USB 拓扑稳定识别两个 CAN 接口,配置 bitrate 并重命名为
#       teleop_double_nero.launch.py 期望的 can_left / can_right.
#
# 本机当前 USB 接线 (用 `ip -details link show canX` 的 parentdev 确认):
#   can0  -> USB 路径 1-5.1:1.0   (Bus1 Port5 Hub Port1)  -> can_left
#   can1  -> USB 路径 1-5.2:1.0   (Bus1 Port5 Hub Port2)  -> can_right
#
# 注意: 本次因 USB 枚举端口变化, 由 1-5.3/1-11 变为 1-5.1/1-5.2.
#       左右臂物理含义沿用旧拓扑推断, 若启动后左右对调, 互换下面两行即可。
#
# 用法: bash can_muti_activate_nero3.sh
# 需要sudo (ip link / modprobe).
# ============================================================================

set -e

# USB 路径 -> 目标 CAN 接口名:bitrate
declare -A USB_PORTS
USB_PORTS["1-5.1:1.0"]="can_left:1000000"
USB_PORTS["1-5.2:1.0"]="can_right:1000000"

echo "🔧 USB_PORTS 映射:"
for k in "${!USB_PORTS[@]}"; do
    echo "  $k -> ${USB_PORTS[$k]}"
done
echo ""

# 1) 加载 gs_usb 内核模块
echo "=== 加载 gs_usb 模块 ==="
sudo modprobe gs_usb || echo "[WARN] gs_usb 模块加载失败(可能已加载)"

# 2) 遍历所有 CAN 接口, 按 USB 路径配置并重命名
echo ""
echo "=== 配置 CAN 接口 ==="
SUCCESS_COUNT=0
for iface in $(ip -br link show type can 2>/dev/null | awk '{print $1}'); do
    # 从 sysfs device 符号链接取 USB 路径 (形如 1-5.3:1.0)
    USB_PATH=$(basename "$(readlink /sys/class/net/$iface/device)" 2>/dev/null)

    echo "--------------------------- $iface (USB: ${USB_PATH:-未知}) ------------------------------"

    if [ -z "$USB_PATH" ]; then
        echo "[ERROR] 无法获取 $iface 的 USB 路径, 跳过"
        continue
    fi

    if [ -n "${USB_PORTS[$USB_PATH]}" ]; then
        IFS=':' read -r TARGET_NAME TARGET_BITRATE <<< "${USB_PORTS[$USB_PATH]}"

        # 检查目标名是否已被占用
        if [ "$iface" != "$TARGET_NAME" ] && ip link show "$TARGET_NAME" &>/dev/null; then
            echo "[WARN] 目标名 $TARGET_NAME 已存在,先删除"
            sudo ip link set "$TARGET_NAME" down 2>/dev/null || true
            sudo ip link delete "$TARGET_NAME" 2>/dev/null || true
        fi

        # 配置 bitrate 并 up
        echo "[INFO] 配置 $iface: bitrate=$TARGET_BITRATE"
        sudo ip link set "$iface" down
        sudo ip link set "$iface" type can bitrate "$TARGET_BITRATE"
        sudo ip link set "$iface" up

        # 重命名为目标名
        if [ "$iface" != "$TARGET_NAME" ]; then
            echo "[INFO] 重命名 $iface -> $TARGET_NAME"
            sudo ip link set "$iface" down
            sudo ip link set "$iface" name "$TARGET_NAME"
            sudo ip link set "$TARGET_NAME" up
        fi

        echo "[INFO] ✅ $USB_PATH -> $TARGET_NAME 配置完成"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "[ERROR] $iface 的 USB 路径 $USB_PATH 不在映射表中"
        echo "        请检查 USB 接线,或更新本脚本的 USB_PORTS"
    fi
done

# 3) 结果
echo ""
echo "=== 配置结果 ==="
ip -br link show type can 2>/dev/null
echo ""
if [ "$SUCCESS_COUNT" -gt 0 ]; then
    echo "[RESULT] ✅ $SUCCESS_COUNT 个 CAN 接口配置成功"
else
    echo "[RESULT] ❌ 没有 CAN 接口匹配成功,请检查 USB 接线"
fi

# 4) 重启后失效提示
echo ""
echo "💡 注意: ip link 配置重启后失效."
echo "   如需开机自动配置,可参考本脚本创建 systemd service 或 udev 规则."
