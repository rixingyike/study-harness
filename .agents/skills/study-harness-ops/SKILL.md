---
name: study-harness-ops
description: Study-Harness 项目专属运维与商业核算技能。当用户需要排查项目运行状况、统计数据库历史会话、核算大模型 Token 成本与省钱策略、或检测 Web 控制台服务状态时自动激活本技能。
version: "1.0.0"
triggers: ["项目体检", "会话统计", "成本核算", "study-harness-ops", "数据库概况"]
---

# Study-Harness 项目专属运维与商业核算技能

本技能是 `study-harness` 项目内置的专属本地 Skill。
当智能体进驻当前项目工作区，遇到数据库状态查询、多轮对话统计、Token 成本折算或 Web 宿主存活排查时，由本技能引导智能体按标准工作流（SOP）进行自动化排查。

## 核心能力与操作指南

### 1. 数据库概况与历史会话统计
当用户询问当前项目有多少会话、数据库运行是否正常时：
```bash
python3 scripts/harness_tools.py summary
```
如需机器解析格式，追加 `--json` 参数。

### 2. Token 成本与套利测算
当用户询问某模型下的 Token 消耗成本或省钱建议时：
```bash
python3 scripts/harness_tools.py cost --model <model_name> --input <in_tokens> --output <out_tokens>
```
* 支持的模型名称：
  * `deepseek`：国产 DeepSeek-V3 API 计费（0.002 / 0.008 元/千Tokens）
  * `claude-pro`：Claude Pro 包月订阅（边际成本 0）
  * `gemini-pro`：Google Gemini / agy 官方额度（边际成本 0）
  * `claude-api`：Claude 3.5 Sonnet 官方 API 直连

### 3. 本地 Web 控制台健康检查
当用户询问前端控制台（端口 3010 / sh.yishulun.com）是否存活时：
```bash
python3 scripts/harness_tools.py status
```

## 输出回复规范
智能体在获取工具返回后，请以专业严谨的格式向用户呈现体检报告：
1. **系统运行概况**（数据库路径、会话总量、消息总量）；
2. **商业成本分析**（按量 vs 包月的成本对比，给出省钱建议）；
3. **服务存活状态**（HTTP 200 响应与健康结论）。
