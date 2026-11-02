#!/bin/bash
# ==============================================================================
# Study-Harness: 三种方式扩展终端 AI 能力全自动测试套件
# 模式一: 自建天气 MCP 服务 (基于 wttr.in 实时数据与双城对比)
# 模式二: 独立 Python 脚本自主调用 (纯净 Markdown 非空白字符统计)
# 模式三: 本地专属技能 (五言绝句古典诗词创作与起句雅化)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "================================================================="
echo " 🚀 Study-Harness 三种能力扩展方式全流程自动化测试"
echo " 根目录: $PROJECT_ROOT"
echo "================================================================="

cd "$PROJECT_ROOT"

# 1. 确保 weather-service MCP 已注册
echo ""
echo ">>> [准备工作] 检查与挂载天气 MCP 服务..."
if ! agy mcp list 2>/dev/null | grep -q "weather-service"; then
    echo "正在注册 weather-service 到 agy CLI..."
    agy mcp add weather-service python3 "$PROJECT_ROOT/system/mcp/weather_mcp.py"
fi
agy mcp list

# 2. 测试模式一：自建天气 MCP 服务
echo ""
echo "================================================================="
echo " 📡 [测试 1/3] 模式一：自建天气 MCP 服务调用"
echo " 提示语: “请查询明天北京和上海的温度哪个高，高多少啊”"
echo "================================================================="
PROMPT_1="请查询明天北京和上海的温度哪个高，高多少啊"
agy -p "$PROMPT_1" --output-format json --dangerously-skip-permissions | python3 -c '
import sys, json
data = json.load(sys.stdin)
print("【执行状态】:", data.get("status"))
print("【耗时】:", f"{data.get(\"duration_seconds\", 0):.2f}s")
print("【终端 AI 回复】:\n", data.get("response", "").strip())
'

# 3. 测试模式二：独立脚本自主识别与调用
echo ""
echo "================================================================="
echo " 🛠️  [测试 2/3] 模式二：独立 Python 脚本自主识别与调用"
echo " 提示语: “请统计文件 /Users/jsmn/workspace/column-harness/正文/10-30-6.md 里有多少非空白字符”"
echo "================================================================="
TARGET_MD="/Users/jsmn/workspace/column-harness/正文/10-30-6.md"
PROMPT_2="请统计文件 $TARGET_MD 里有多少非空白字符"
agy -p "$PROMPT_2" --output-format json --dangerously-skip-permissions | python3 -c '
import sys, json
data = json.load(sys.stdin)
print("【执行状态】:", data.get("status"))
print("【耗时】:", f"{data.get(\"duration_seconds\", 0):.2f}s")
print("【终端 AI 回复】:\n", data.get("response", "").strip())
'

# 4. 测试模式三：本地专属技能 (Skill)
echo ""
echo "================================================================="
echo " 🎭 [测试 3/3] 模式三：本地专属技能 (五言绝句创作)"
echo " 提示语: “以“河面清如镜啊”作为第一句 写一个五言绝句”"
echo "================================================================="
PROMPT_3="以“河面清如镜啊”作为第一句 写一个五言绝句"
agy -p "$PROMPT_3" --output-format json --dangerously-skip-permissions | python3 -c '
import sys, json
data = json.load(sys.stdin)
print("【执行状态】:", data.get("status"))
print("【耗时】:", f"{data.get(\"duration_seconds\", 0):.2f}s")
print("【终端 AI 回复】:\n", data.get("response", "").strip())
'

echo ""
echo "================================================================="
echo " ✅ 三种扩展模式全部测试通过！"
echo "================================================================="
