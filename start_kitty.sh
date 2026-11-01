#!/bin/bash
# ==============================================================================
# 极简版 Kitty + tmux 终端启动脚本 (专栏《打造属于你自己的智能体 Harness》第 4 讲配套)
# 作用：启动带 IPC 远程控制的 Kitty 终端，内置 tmux workspace 会话，实现终端 AI 的稳定复用
# ==============================================================================
set -e

SOCK_PATH="${HOME}/.kitty.sock"
SOCK="unix:${SOCK_PATH}"
SESSION_NAME="workspace"

# 1. 清理异常断电或退出时残留的旧 socket 文件
rm -f "$SOCK_PATH"

echo "🚀 启动 Kitty 终端 (IPC Socket: $SOCK, tmux: $SESSION_NAME)..."

# 2. 核心启动：无桌面 Linux 环境借助 xvfb-run 提供虚拟屏幕渲染，本地桌面环境直接启动
if [ -z "$DISPLAY" ] && command -v xvfb-run >/dev/null 2>&1; then
    exec xvfb-run -a -s "-screen 0 1024x768x24" kitty -o allow_remote_control=yes --listen-on="$SOCK" tmux new-session -A -s "$SESSION_NAME"
else
    exec kitty -o allow_remote_control=yes --listen-on="$SOCK" tmux new-session -A -s "$SESSION_NAME"
fi
