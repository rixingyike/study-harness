#!/usr/bin/env python3
"""
Study-Harness 方案 A: 基于标准 MCP (Model Context Protocol) 协议的自定义业务工具服务
让终端 AI (agy CLI / Claude Code) 能够自动跨进程调用我们代码里定义的专属业务函数
"""
import os
import sys
import json
import sqlite3
from pathlib import Path

# 兼容 mcp 2.x 与 1.x
try:
    from mcp.server.mcpserver import MCPServer
    app = MCPServer("study-harness-tools")
except ImportError:
    try:
        from mcp.server.fastmcp import FastMCP
        app = FastMCP("study-harness-tools")
    except Exception as e:
        print(f"Error importing MCP server: {e}", file=sys.stderr)
        sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "chat_web" / "backend" / "chat.db"

@app.tool()
def get_study_harness_summary() -> str:
    """获取当前 Study-Harness 项目的运行状态、历史会话数与消息总数"""
    if not DB_PATH.exists():
        return f"项目数据库未初始化 (路径: {DB_PATH})"
    try:
        conn = sqlite3.connect(DB_PATH)
        sess_count = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        recent_sessions = conn.execute(
            "SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC LIMIT 3"
        ).fetchall()
        conn.close()

        summary = {
            "status": "online",
            "db_path": str(DB_PATH),
            "total_sessions": sess_count,
            "total_messages": msg_count,
            "recent_sessions": [
                {"id": r[0], "title": r[1], "updated_at": r[2]} for r in recent_sessions
            ]
        }
        return json.dumps(summary, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"查询数据库异常: {str(e)}"

@app.tool()
def calculate_token_cost(model_name: str, input_tokens: int, output_tokens: int) -> str:
    """
    根据专栏第 04 讲的国内外大模型价格公式，计算指定 Token 消耗在不同模型下的成本折算
    """
    model_lower = model_name.lower()
    rates = {
        "deepseek": {"in": 0.002, "out": 0.008, "currency": "RMB", "desc": "国产 DeepSeek-V3 API (元/千Tokens)"},
        "claude-pro": {"in": 0.0, "out": 0.0, "currency": "USD", "desc": "Claude Pro 包月订阅 (固定约 $20/月，边际成本 0)"},
        "gemini-pro": {"in": 0.0, "out": 0.0, "currency": "USD", "desc": "Google AI Pro / agy CLI 官方额度复用 (边际成本 0)"},
        "claude-api": {"in": 0.021, "out": 0.105, "currency": "RMB", "desc": "Claude 3.5 Sonnet 官方 API 直连 (约 3/15 美元/M Tokens)"}
    }

    match_key = "deepseek"
    for k in rates:
        if k in model_lower:
            match_key = k
            break

    r = rates[match_key]
    cost = (input_tokens / 1000.0) * r["in"] + (output_tokens / 1000.0) * r["out"]
    return (
        f"【Token 计费核算 - {r['desc']}】\n"
        f"输入: {input_tokens:,} Tokens | 输出: {output_tokens:,} Tokens\n"
        f"单次估算成本: {cost:.4f} {r['currency']}\n"
        f"省钱建议: 推荐重度开发走包月/终端 CLI 复用路线，日常微调走 DeepSeek 按量路线。"
    )

if __name__ == "__main__":
    # 以标准 stdio 方式启动 MCP 服务
    app.run(transport="stdio")
