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

# ----------------- 专栏第 07 讲配套：科学家性格、异构双智能体与战略战术评估 -----------------

@app.tool()
def profile_scientist(profile_text: str, scholar_name: str = "研创学者", output_file: str = "") -> str:
    """
    【第 07 讲配套】科学家性格画像与潜能诊断引擎 (scientist-profiler)
    基于《科学研究的艺术》第十一章「科学家」，从反应型/被动型人格、爱因斯坦科研三分法、
    出洋相心理韧性、推测型/条理型谱系进行客观诊断 (执行温度 0.2)。
    
    参数:
        profile_text: 学者的经历自述、科研笔记、日常习惯或工作总结
        scholar_name: 学者姓名或代号 (默认 "研创学者")
        output_file: 可选的 Markdown 报告保存路径 (如 认知/学者性格画像.md)
    """
    try:
        from scripts.scientist_profiler import profile_scientist as run_profile
        res = run_profile(profile_text, scholar_name=scholar_name, output_path=output_file or None)
        saved_msg = f"\n\n[+] 报告已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["report"] + saved_msg
    except Exception as e:
        return f"科学家性格诊断执行异常: {str(e)}"

@app.tool()
def collaborate_duo(topic_or_spark: str, max_rounds: int = 1, output_file: str = "") -> str:
    """
    【第 07 讲配套】推测型与条理型异构双智能体协同器 (speculative-systematic-duo)
    基于《科学研究的艺术》第十一章推测型（巴斯德浪漫派）与条理型（工匠古典派）黄金协同机制。
    浪漫派（温度 0.8）直觉跳跃突破思维死角，条理派（温度 0.2）冷面审查锻造可落地实验 SOP。
    
    参数:
        topic_or_spark: 拟研究的课题靶点、初始灵感或技术难题
        max_rounds: 交互轮次 (默认 1)
        output_file: 可选的 Markdown 协同专报保存路径
    """
    try:
        from scripts.speculative_systematic_duo import collaborate_duo as run_duo
        res = run_duo(topic_or_spark, max_rounds=max_rounds, output_path=output_file or None)
        saved_msg = f"\n\n[+] 协同专报已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["full_report"] + saved_msg
    except Exception as e:
        return f"双智能体协同推演执行异常: {str(e)}"

@app.tool()
def evaluate_topic(topic_description: str, topic_title: str = "拟研课题", output_file: str = "") -> str:
    """
    【第 07 讲配套】课题战略审查与四维打分引擎 (topic-evaluator)
    基于《科学研究的艺术》第十章「战略和战术」的辩证平衡哲学，对课题方案进行四维审查并给出百分制评分 (执行温度 0.2)。
    审查维度：三级计划分权 (30分)、理论与应用互哺 (25分)、探索性与发展性配比 (25分)、战略性搁置与止损机制 (20分)。
    
    参数:
        topic_description: 课题的目标、技术路线、人员分工或立项规划说明
        topic_title: 课题名称或代号 (默认 "拟研课题")
        output_file: 可选的 Markdown 审查报告保存路径 (如 认知/课题战略审查报告.md)
    """
    try:
        from scripts.topic_evaluator import evaluate_topic as run_eval
        res = run_eval(topic_description, topic_title=topic_title, output_path=output_file or None)
        saved_msg = f"\n\n[+] 课题审查报告已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["report"] + saved_msg
    except Exception as e:
        return f"课题战略审查执行异常: {str(e)}"

if __name__ == "__main__":
    # 以标准 stdio 方式启动 MCP 服务
    app.run(transport="stdio")
