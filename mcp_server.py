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

# ----------------- 专栏第 07 讲配套：异构双智能体协同与课题打分 (MCP 服务工具) -----------------

def _load_skill_script(skill_name: str, script_name: str):
    """动态加载 system/skills/<skill-name>/scripts/<script_name>.py 模块"""
    import importlib.util
    script_path = PROJECT_ROOT / "system" / "skills" / skill_name / "scripts" / f"{script_name}.py"
    if not script_path.exists():
        # 回退兼容 scripts/ 目录
        script_path = PROJECT_ROOT / "scripts" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(f"{skill_name}_{script_name}", script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

@app.tool()
def collaborate_duo(topic_or_spark: str, max_rounds: int = 1, output_file: str = "") -> str:
    """
    【第 07 讲配套 MCP 工具】推测型与条理型异构双智能体协同器 (speculative-systematic-duo)
    基于《科学研究的艺术》第十一章推测型（巴斯德浪漫派）与条理型（工匠古典派）黄金协同机制。
    浪漫派（温度 0.8）直觉跳跃突破思维死角，条理派（温度 0.2）冷面审查锻造可落地实验 SOP。
    
    参数:
        topic_or_spark: 拟研究的课题靶点、初始灵感或技术难题
        max_rounds: 交互轮次 (默认 1)
        output_file: 可选的 Markdown 协同专报保存路径
    """
    try:
        mod = _load_skill_script("speculative-systematic-duo", "duo")
        res = mod.collaborate_duo(topic_or_spark, max_rounds=max_rounds, output_path=output_file or None)
        saved_msg = f"\n\n[+] 协同专报已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["full_report"] + saved_msg
    except Exception as e:
        return f"双智能体协同推演执行异常: {str(e)}"

@app.tool()
def evaluate_topic(topic_description: str, topic_title: str = "拟研课题", output_file: str = "") -> str:
    """
    【第 07 讲配套 MCP 工具】课题战略审查与四维打分引擎 (topic-evaluator)
    基于《科学研究的艺术》第十章「战略和战术」的辩证平衡哲学，对课题方案进行四维审查并给出百分制评分 (执行温度 0.2)。
    审查维度：三级计划分权 (30分)、理论与应用互哺 (25分)、探索性与发展性配比 (25分)、战略性搁置与止损机制 (20分)。
    
    参数:
        topic_description: 课题的目标、技术路线、人员分工或立项规划说明
        topic_title: 课题名称或代号 (默认 "拟研课题")
        output_file: 可选的 Markdown 审查报告保存路径 (如 认知/课题战略审查报告.md)
    """
    try:
        mod = _load_skill_script("topic-evaluator", "evaluator")
        res = mod.evaluate_topic(topic_description, topic_title=topic_title, output_path=output_file or None)
        saved_msg = f"\n\n[+] 课题审查报告已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["report"] + saved_msg
    except Exception as e:
        return f"课题战略审查执行异常: {str(e)}"

# ----------------- 专栏第 08 讲配套：闪念反刍随身记与双智能体推理 (MCP 服务工具) -----------------

@app.tool()
def ruminate_spark(spark_text: str, category: str = "闪念", tags: str = "") -> str:
    """
    【第 08 讲配套 MCP 工具】反刍随身记与闪念捕获服务 (intuition-ruminator)
    基于《科学研究的艺术》第六章「直觉」之加压-泄压与随身纸笔置于脑后（Unload）。
    将灵光一现的顿悟瞬间存入 反刍/YYYY-MM-DD.md 并清空工作记忆缓存，静待潜意识拼图。
    
    参数:
        spark_text: 脑海中蹦出的直觉闪念、反常假说或微小灵感
        category: 类别标签 (默认 "闪念", 可选 "假说", "线索", "灵感")
        tags: 关键词标签 (如 "大模型, 潜意识")
    """
    try:
        from system.scripts.ruminator import record_spark
        return record_spark(spark_text, category=category, tags=tags, root_dir=PROJECT_ROOT)
    except Exception as e:
        return f"闪念捕获执行异常: {str(e)}"

@app.tool()
def get_daily_rumination(date_str: str = "") -> str:
    """
    【第 08 讲配套 MCP 工具】读取指定日期的反刍闪念日志 (格式 YYYY-MM-DD，留空则读取今日)
    """
    try:
        from system.scripts.ruminator import read_daily_rumination
        return read_daily_rumination(date_str=date_str, root_dir=PROJECT_ROOT)
    except Exception as e:
        return f"读取反刍日志异常: {str(e)}"

@app.tool()
def dual_agent_reason(clue_or_premise: str, output_file: str = "") -> str:
    """
    【第 08 讲配套 MCP 工具】侦探与法官双智能体推演服务 (dual-agent-reasoning)
    基于《科学研究的艺术》第七章「推理」之侦探与法官职能严格分离。
    敏锐侦探（温度 0.8）根据模糊线索大胆设想因果分支；冷面法官（温度 0.2）冷酷排伪并输出闭环裁决。
    
    参数:
        clue_or_premise: 待推演的案件线索、业务死锁或待求证课题前提
        output_file: 可选的 Markdown 推演专报保存路径 (如 假说/推演方案.md)
    """
    try:
        from system.scripts.dual_reasoner import dual_agent_reason as run_reasoning
        res = run_reasoning(clue_or_premise, output_path=output_file or None)
        saved_msg = f"\n\n[+] 推演专报已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["full_report"] + saved_msg
    except Exception as e:
        return f"双智能体推演执行异常: {str(e)}"

# ----------------- 专栏第 09 讲配套：青霉素反常机遇与张伯伦多假说打擂 (MCP 服务工具) -----------------

@app.tool()
def detect_serendipity(anomaly_description: str, context: str = "", output_file: str = "") -> str:
    """
    【第 09 讲配套 MCP 工具】青霉素反常机遇洞察服务 (serendipity-radar)
    基于《科学研究的艺术》第三章「机遇」之巴斯德定律与反常机遇深挖。
    将实验报错、意外污染、离群反常数据当成真理敲门的请柬，逆向探查颠覆性机理与突破假说 (执行温度 0.6)。
    
    参数:
        anomaly_description: 遭遇的反常报错、意外事故、离群非预期数据说明
        context: 实验背景、既有操作与原本预期 (可选)
        output_file: 可选的 Markdown 洞察专报保存路径 (如 认知/反常机遇专报.md)
    """
    try:
        from system.scripts.serendipity_radar import detect_serendipity as run_detect
        res = run_detect(anomaly_description, context=context, output_path=output_file or None)
        saved_msg = f"\n\n[+] 机遇洞察专报已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["report"] + saved_msg
    except Exception as e:
        return f"反常机遇洞察执行异常: {str(e)}"

@app.tool()
def chamberlin_hypotheses(problem_or_phenomenon: str, hypothesis_count: int = 3, output_file: str = "") -> str:
    """
    【第 09 讲配套 MCP 工具】张伯伦多假说打擂服务 (chamberlin-hypotheses)
    基于《科学研究的艺术》第四章「假说」之张伯伦多工作假说原则 (避免沦为单一假说的奴隶)。
    并发生成多个互不兼容、切入角度完全不同的竞争假说，并设计排他性判决实验让其同台打擂 (执行温度 0.7)。
    
    参数:
        problem_or_phenomenon: 待破解的核心难题、反常现象或业务命题
        hypothesis_count: 并发生成的假说数量 (默认 3，可选 3-5)
        output_file: 可选的 Markdown 打擂专报保存路径 (如 假说/多假说打擂专报.md)
    """
    try:
        from system.scripts.chamberlin import generate_chamberlin_hypotheses as run_chamberlin
        res = run_chamberlin(problem_or_phenomenon, hypothesis_count=hypothesis_count, output_path=output_file or None)
        saved_msg = f"\n\n[+] 多假说打擂专报已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["report"] + saved_msg
    except Exception as e:
        return f"多假说打擂执行异常: {str(e)}"

# ----------------- 专栏第 10 讲配套：求证探索与五步流水线总控 (MCP 服务工具) -----------------

@app.tool()
def verify_fact_or_code(claim_or_code: str, verification_type: str = "fact", topic_name: str = "待求证条目", output_file: str = "") -> str:
    """
    【第 10 讲配套 MCP 工具】事实与代码求证探索服务 (fact-code-verifier)
    基于五步研创法 Step 2「一手资料与初步探针」与毛泽东《实践论》实践求证。
    拒绝道听途说，对文本事实主张进行权威基线比对与反例审计；对代码片段进行独立沙箱实测，捕获真实输出与耗时 (执行温度 0.2)。
    
    参数:
        claim_or_code: 待核验的事实主张文本，或待运行实测的 Python 代码片段
        verification_type: 核验类型，"fact" (文本事实核验) 或 "code" (代码运行探针，默认 "fact")
        topic_name: 待核验主题代号或名称 (默认 "待求证条目")
        output_file: 可选的 Markdown 求证笔记保存路径 (如 笔记/求证笔记.md)
    """
    try:
        from system.scripts.fact_code_verifier import verify_claim_or_code as run_verify
        res = run_verify(claim_or_code, verification_type=verification_type, topic_name=topic_name, output_file=output_file or "")
        saved_msg = f"\n\n[+] 求证笔记已归档至: {res['saved_path']}" if res.get('saved_path') else ""
        return res["report"] + saved_msg
    except Exception as e:
        return f"实证求证执行异常: {str(e)}"

@app.tool()
def inspect_study_pipeline(workspace_path: str = "") -> str:
    """
    【第 10 讲配套 MCP 工具】五步研创流水线总控与体检服务 (study-harness-pipeline)
    基于毛泽东《实践论》“实践-认识-再实践-再认识”闭环总控与五步研创法。
    全面体检工作区五大核心目录 (资料/ 笔记/ 认知/ 假说/ 记录/) 的流转状态、关键标桩文件与流通文档总量，诊断当前研发卡点并输出下一步建议 SOP。
    
    参数:
        workspace_path: 可选的研创工作区路径，留空则默认检测当前项目根目录
    """
    try:
        from system.scripts.pipeline_coordinator import inspect_study_pipeline as run_inspect
        return run_inspect(workspace_path=workspace_path)
    except Exception as e:
        return f"流水线体检诊断异常: {str(e)}"

if __name__ == "__main__":
    # 以标准 stdio 方式启动 MCP 服务
    app.run(transport="stdio")
