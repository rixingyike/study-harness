#!/usr/bin/env python3
"""
Study-Harness 方案 B: 独立命令行脚本工具 (Scripting & CLI / Skill 工具化)
专为终端 AI Agent (agy CLI, Claude Code, Codex, 终端 Bash) 设计的即插即用业务工具库。
无需配置 MCP 守护进程，终端 AI 直接使用 Bash 工具执行本脚本即可完成专属业务调用。
"""
import sys
import os
import argparse
import json
import sqlite3
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "chat_web" / "backend" / "chat.db"

def cmd_summary(args):
    """统计项目数据库运行状态"""
    if not DB_PATH.exists():
        print(f"[!] 数据库文件不存在: {DB_PATH}", file=sys.stderr)
        return 1
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        total_sessions = cur.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        total_messages = cur.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        recent = cur.execute("SELECT id, title, updated_at FROM sessions ORDER BY updated_at DESC LIMIT 5").fetchall()
        conn.close()

        res = {
            "status": "online",
            "db_path": str(DB_PATH),
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "recent_sessions": [
                {"id": r[0], "title": r[1], "updated_at": r[2]} for r in recent
            ]
        }
        if args.json:
            print(json.dumps(res, ensure_ascii=False, indent=2))
        else:
            print(f"=== Study-Harness 数据库概况 ===")
            print(f"数据库路径: {DB_PATH}")
            print(f"总会话数  : {total_sessions}")
            print(f"总消息数  : {total_messages}")
            print(f"\n--- 最近会话 ---")
            for r in recent:
                print(f"• [{r[0][:8]}] {r[1]} ({r[2]})")
        return 0
    except Exception as e:
        print(f"[!] 查询失败: {e}", file=sys.stderr)
        return 1

def cmd_cost(args):
    """根据第四篇公式折算各模型 Token 成本"""
    model_lower = args.model.lower()
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
    cost = (args.input_tokens / 1000.0) * r["in"] + (args.output_tokens / 1000.0) * r["out"]
    
    if args.json:
        data = {
            "model": args.model,
            "matched_plan": match_key,
            "description": r["desc"],
            "input_tokens": args.input_tokens,
            "output_tokens": args.output_tokens,
            "estimated_cost": round(cost, 6),
            "currency": r["currency"]
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"【Token 计费核算 - {r['desc']}】")
        print(f"输入: {args.input_tokens:,} Tokens | 输出: {args.output_tokens:,} Tokens")
        print(f"单次成本: {cost:.4f} {r['currency']}")
        print(f"省钱建议: 推荐重度日常开发走包月终端 CLI 渠道，按量调测走 DeepSeek。")
    return 0

def cmd_status(args):
    """检测 Web 宿主进程 (port 3010) 健康状态"""
    url = f"http://127.0.0.1:{args.port}/api/health"
    try:
        req = urllib.request.urlopen(url, timeout=3)
        body = req.read().decode('utf-8')
        print(f"Web 状态: 在线 (200 OK) -> {body.strip()}")
        return 0
    except Exception as e:
        print(f"Web 状态: 未响应 (http://127.0.0.1:{args.port}) - {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(
        description="Study-Harness 命令行业务工具集 (方案 B: CLI Script)",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="子命令")

    # summary
    p_summary = subparsers.add_parser("summary", help="查看数据库与会话统计")
    p_summary.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    p_summary.set_defaults(func=cmd_summary)

    # cost
    p_cost = subparsers.add_parser("cost", help="核算 Token 成本及套利测算")
    p_cost.add_argument("--model", default="deepseek", help="模型名称 (deepseek, claude-pro, gemini-pro, claude-api)")
    p_cost.add_argument("--input", dest="input_tokens", type=int, default=1000, help="输入 Token 数")
    p_cost.add_argument("--output", dest="output_tokens", type=int, default=500, help="输出 Token 数")
    p_cost.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    p_cost.set_defaults(func=cmd_cost)

    # status
    p_status = subparsers.add_parser("status", help="检查本地 Web 服务 (port 3010) 健康状态")
    p_status.add_argument("--port", type=int, default=3010, help="服务端口")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    sys.exit(args.func(args))

if __name__ == "__main__":
    main()
