#!/bin/bash
# ==============================================================================
# 极简版 Kitty + tmux 终端守护启动脚本 (专栏《打造属于你自己的智能体 Harness》第 4 讲配套)
# 作用：启动带 IPC 远程控制的 Kitty 终端，内置 tmux workspace 会话，实现终端 AI 的稳定复用
# 特性：支持 systemd 开机自启、实例防重检测、失效死 Socket 自愈清理、无头服务器虚拟渲染
# ==============================================================================
set -e

SOCK_PATH="${HOME}/.kitty.sock"
SOCK="unix:${SOCK_PATH}"
SESSION_NAME="${KITTY_TMUX_SESSION:-workspace}"

# 1. 活跃检测与防冲突：若已有活跃实例在运行，直接提示并安全退出
if [ -S "$SOCK_PATH" ] || [ -e "$SOCK_PATH" ]; then
    if kitten @ --to "$SOCK" ls >/dev/null 2>&1; then
        echo "✅ Kitty 实例已在后台运行中 (Socket: $SOCK_PATH)，无需重复启动。"
        echo "💡 直接执行接入：tmux attach -t $SESSION_NAME"
        exit 0
    fi
    # 若是宕机或异常断电留下的失效死 Socket，自动清理
    echo "⚠️ 检测到残留的失效 socket，正在清理: $SOCK_PATH"
    rm -f "$SOCK_PATH"
fi

echo "🚀 正在启动 Kitty 终端 (IPC: $SOCK, tmux: $SESSION_NAME)..."

# 2. 核心启动：无桌面 Linux 环境借助 xvfb-run 提供虚拟帧缓冲；本地桌面直接启动
if [ -z "$DISPLAY" ] && command -v xvfb-run >/dev/null 2>&1; then
    exec xvfb-run -a -s "-screen 0 1024x768x24" kitty -o allow_remote_control=yes --listen-on="$SOCK" tmux new-session -A -s "$SESSION_NAME"
else
    exec kitty -o allow_remote_control=yes --listen-on="$SOCK" tmux new-session -A -s "$SESSION_NAME"
fi
