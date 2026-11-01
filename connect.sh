#!/bin/bash
# ==============================================================================
# macOS 本地一键直连云端 AI 终端工作区脚本 (Study-Harness 第 04 讲配套)
# 作用：通过 SSH 密钥认证，一条指令直达云端服务器的 tmux workspace 会话
# 使用方法：
#   1. 修改下方 SERVER_IP 为你的云服务器公网 IP (或通过环境变量 SERVER_IP=xxx ./connect.sh 传入)
#   2. chmod +x ./connect.sh
#   3. 执行 ./connect.sh 即可秒级进入云端 AI 终端
# ==============================================================================

SERVER_USER="${SERVER_USER:-ubuntu}"
SERVER_IP="${SERVER_IP:-127.0.0.1}" # 请替换为你的云服务器真实公网 IP
PORT="${SERVER_PORT:-22}"

if [ "$SERVER_IP" = "127.0.0.1" ]; then
    echo "💡 提示: 请先将脚本中的 SERVER_IP 修改为你实际的云服务器公网 IP，或通过环境变量指定："
    echo "   SERVER_IP=123.45.67.89 ./connect.sh"
    echo ""
fi

echo "🌐 正在一键直连云端 AI 终端 (${SERVER_USER}@${SERVER_IP}:${PORT})..."

# -t 参数强制分配伪终端（PTY），并在登录后直接接入已常驻的 tmux workspace 会话
exec ssh -t -p "$PORT" "${SERVER_USER}@${SERVER_IP}" "tmux attach -t workspace"
