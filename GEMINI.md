# Study-Harness 智能体系统规范与脚本清单 (Agent Manifest)

本项目为开发者提供了标准的私有能力扩展目录体系 `system/`：

## 1. 系统专有脚本工具集 (System Scripts)
存放于 `system/scripts/` 目录，AI 可根据意图自主识别并直接调用：
- `python3 system/scripts/count_markdown_chars.py <file_path>`:
  【用途】精准统计 Markdown 文件的纯净非空白字符总数。
  【过滤规则】自动跳过开头的 YAML Frontmatter、排除所有的 `>` 引用块、排除所有的 ```` 代码块，仅统计有效正文文本的非空白字符。
  【自主调用策略】当用户询问某 Markdown 文件（提供路径）有多少非空白字符或有效字数时，智能体必须主动调用本脚本执行统计，并如实汇报脚本返回的数据。

## 2. 系统 MCP 服务 (System MCP)
存放于 `system/mcp/` 目录：
- `weather_mcp.py` (weather-service): 查询实时天气与明日温度对比 (基于 wttr.in)。

## 3. 系统专用技能 (System Skills)
存放于 `system/skills/` 目录：
- `quatrain-poet`: 五言绝句古典诗词创作。
