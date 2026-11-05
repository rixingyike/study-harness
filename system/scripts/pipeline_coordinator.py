#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pipeline_coordinator.py: 五步研创流水线总控与体检服务核心实现 (MCP study-harness-pipeline 配套)
理论依据：五步研创法与毛泽东《实践论》“实践-认识-再实践-再认识”闭环总控
"""

import os
import sys
import datetime
from pathlib import Path
from typing import Dict, Any, List

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

# 五步研创法核心目录规范
PIPELINE_DIRS = [
    ("资料", "Step 1: 批判性文献审阅与感性输入", "不完美.md"),
    ("笔记", "Step 2: 一手资料探针与代码实证求证", ""),
    ("认知", "Step 3: 巴克罗夫特极简飞刀与理性跃迁", "标签.md"),
    ("假说", "Step 4: 张伯伦多假说打擂与实验策划", ""),
    ("记录", "Step 5: 达尔文打脸反常记录与实证沉淀", "达尔文打脸笔记.md")
]

def inspect_study_pipeline(workspace_path: str = "") -> str:
    """
    对研创工作区的五大核心目录及流水线状态进行全生命周期体检与推进诊断
    """
    root = Path(workspace_path) if workspace_path else PROJECT_ROOT
    if not root.is_absolute():
        root = PROJECT_ROOT / root
        
    status_lines = []
    status_lines.append(f"# Study-Harness 五步研创流水线健康度与推进诊断专报")
    status_lines.append(f"\n> 理论依据：毛泽东《实践论》认识论闭环与五步研创工程 SOP")
    status_lines.append(f"> 检查时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    status_lines.append(f"> 工作区根目录：`{root}`\n")
    
    total_files = 0
    dir_stats = []
    
    for dir_name, desc, key_file in PIPELINE_DIRS:
        d_path = root / dir_name
        exists = d_path.exists() and d_path.is_dir()
        files = list(d_path.glob("*.md")) if exists else []
        count = len(files)
        total_files += count
        has_key = (d_path / key_file).exists() if (exists and key_file) else False
        
        dir_stats.append({
            "name": dir_name,
            "desc": desc,
            "exists": exists,
            "count": count,
            "files": [f.name for f in files[:5]],
            "key_file": key_file,
            "has_key": has_key
        })
        
    # 状态表格
    status_lines.append("## 一、五大目录流转状态矩阵\n")
    status_lines.append("| 目录阶段 | 对应研创步骤 | 目录状态 | Markdown 文档数 | 关键标桩文件状态 |")
    status_lines.append("| :--- | :--- | :--- | :--- | :--- |")
    
    for st in dir_stats:
        state_icon = "✅ 已就绪" if st["exists"] else "⚠️ 未建立"
        key_icon = f"✅ `{st['key_file']}` 存在" if st["has_key"] else (f"❌ 缺少 `{st['key_file']}`" if st["key_file"] else "—")
        status_lines.append(f"| `{st['name']}/` | {st['desc']} | {state_icon} | {st['count']} 篇 | {key_icon} |")
        
    # 推进研判与瓶颈定位
    status_lines.append("\n## 二、当前研创阶段研判与卡点诊断\n")
    
    # 逻辑判断当前主战阶段
    s1 = dir_stats[0]["count"]
    s2 = dir_stats[1]["count"]
    s3 = dir_stats[2]["count"]
    s4 = dir_stats[3]["count"]
    s5 = dir_stats[4]["count"]
    
    action_items = []
    
    if s1 == 0:
        current_phase = "阶段 1：感性输入盲区（尚未导入初始资料）"
        action_items.append("立即使用 `critical-reader` 技能导入目标专著或前沿文献，重点生成 `资料/不完美.md`。")
    elif not dir_stats[0]["has_key"]:
        current_phase = "阶段 1：资料收集中，但缺少靶点标桩"
        action_items.append("已有文献输入，但缺少 `资料/不完美.md`；建议运行 `critical-reader` 提炼知识空白与内在矛盾。")
    elif s2 == 0:
        current_phase = "阶段 2：一手求证滞后（缺乏实证与代码探针）"
        action_items.append("针对 `资料/不完美.md` 中暴露的疑点，调用 `fact-code-verifier` MCP 服务执行一手代码或事实探针。")
    elif s3 == 0:
        current_phase = "阶段 3：认知尚未收敛提炼"
        action_items.append("调用 `barcroft-cleaver` 技能对已有一手笔记进行外科手术式拆解，锁定主要矛盾并建立 `认知/标签.md`。")
    elif s4 == 0:
        current_phase = "阶段 4：假说打擂与验证准备期"
        action_items.append("基于核心认知，调用 `chamberlin-hypotheses` MCP 服务并发生成多重假说打擂，并用 `experiment-planner` 制定 Pilot 试点。")
    else:
        current_phase = "阶段 5：螺旋闭环推进与成稿沉淀期"
        action_items.append("持续保持 `darwin-critic-observer` 挑刺监听，将经受住实证检验的成果沉淀为正式产出。")
        
    status_lines.append(f"- **主导研发态势**：**{current_phase}**")
    status_lines.append(f"- **流水线流通文档总量**：共计 {total_files} 篇规范研创 Markdown 文档。")
    
    # 下一步建议行动指令集
    status_lines.append("\n## 三、实践论闭环行动指南（下一步建议 SOP）\n")
    for idx, act in enumerate(action_items, 1):
        status_lines.append(f"{idx}. {act}")
        
    status_lines.append("\n> 提示：保持轻量纯文本哲学，每个阶段产物严格向下游输送，绝不越级跳步，让数字外骨骼守护你的专注心智。")
    
    return "\n".join(status_lines)
