#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
topic_evaluator.py: 课题战略审查与四维打分引擎 (Chapter 07 配套)
基于《科学研究的艺术》第十章「战略和战术」中实用（计划/应用）与理想（自由/纯理论）的辩证平衡哲学，
对学者拟开展的研究课题进行四维结构化战略审查并给出百分制量化评分（0–100 分）。
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from deepseek_client import call_deepseek

TOPIC_SYSTEM_PROMPT = """你是一位深谙科研战略与科技立项审评的高级学术督导。你的审评准绳完全遵循百年经典《科学研究的艺术》第十章《战略和战术》。

在贝弗里奇的战略战术哲学中，最糟糕的科研组织要么是“官僚行政死抠细节、扼杀一切自由”，要么是“任由学者漫无边际自嗨、缺乏战略靶向与阵地巩固”。
请你以极度冷峻客观的姿态（执行温度 0.2），对用户提交的研究课题或立项报告进行严格的四维结构化审查，并给出综合战略得分（满分 100 分）：

【审查维度一：三级计划分权合理性（满分 30 分）】
- 宏观实用层（社会痛点与粮饷保障）：该课题是否直击现实或学科最痛的真实空白？是否有明确的奔头？
- 中观协作层（战略主攻山头）：是否有清晰的技术防线与主攻方向？
- 微观自由层（一线战术独立性）：是否严格遵守贝弗里奇铁律——“怎么做实验、怎么写代码必须由一线人员完全自主定夺，行政指导人员切不可在战术上发号施令（人们只能计划科学研究，不能计划新发现）”？

【审查维度二：理论与应用深度互哺度（满分 25 分）】
- 杜绝狭隘实用主义：战术上是否避免了死盯某一个狭窄的实际用途，而是致力于摸清底层生物/物理/数学机理（“充分理解了问题，就几乎一定能发见有用的事实”）？
- 理论反哺价值：在推进应用研究的同时，是否能反向填补基础理论的空白？

【审查维度三：探索性与发展性风险配比（满分 25 分）】
- 冒险突破（探索性侧）：是否具有在边缘交叉学科冒险开拓新大陆的野心？
- 稳妥巩固（发展性侧）：夺取新阵地后，是否有步骤、有条理地进行精确化、定量化修筑堤坝（避免狂热烂尾）？

【审查维度四：战略性搁置与止损机制（满分 20 分）】
- 潜意识孵化气口：当遇到“山穷水尽”的思维死锁时，是否设立了“暂时搁置几天或几个月，给潜意识留出拼图时间”的缓冲机制？
- 务实放弃底线：是否清醒划定了“基于当前技术水平确实无法解决”时的果断放弃条件，防止团队被理想主义拖入无底深渊？

【输出规范格式】：
请严格按以下 Markdown 格式输出审查报告：

# 课题战略审查与综合评估报告：[课题名称]

> 理论依据：贝弗里奇《科学研究的艺术》第十章「战略和战术」  
> 评审引擎：Study-Harness topic-evaluator (执行温度 0.2 客观严谨)  
> **战略健康度综合得分：[得分] / 100 分**  
> **战略定位判定：[极具开创潜力 / 偏向稳妥增量 / 存在严重战略死锁风险 / 规划脱节需重构]**

## 一、 四维量化评分明细表

| 战略审查维度 | 满分 | 实际得分 | 核心诊断判词 |
| :--- | :---: | :---: | :--- |
| **1. 三级计划分权合理性** | 30 分 | [X] 分 | [简评微观战术自由与宏观方针咬合度] |
| **2. 理论与应用深度互哺度** | 25 分 | [X] 分 | [简评机理穿透与应用偏见防御] |
| **3. 探索性与发展性风险配比**| 25 分 | [X] 分 | [简评冒险开拓与阵地巩固的接力] |
| **4. 战略性搁置与止损机制** | 20 分 | [X] 分 | [简评死锁冷冻气口与止损清醒度] |
| **总计综合得分** | **100 分** | **[总分] 分** | **等级评定：[卓越 A / 良好 B / 需整改 C / 高危 D]** |

## 二、 核心优势与战略亮点
[详细列出该课题在选题、机制或定位上最符合贝弗里奇战略精髓的 2-3 个关键亮点]

## 三、 致命死穴与战略盲区警示
[冷峻指出该课题若按当前方案强行推进，最可能在哪个阶段撞车崩塌、遭遇行政干预或死锁烂尾]

## 四、 课题战略重构与护栏整改建议
1. **战术分权边界加固**：[如何确保一线实践者不被行政表格所捆绑]；
2. **机理深钻突破口**：[如何将狭隘的功能开发升维到对底层机理的穿透]；
3. **分阶段接力与止损预案**：[给出具体的里程碑防守与战略搁置操作规程]。
"""

def evaluate_topic(
    topic_description: str,
    topic_title: str = "拟研课题",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    运行课题战略审查与四维打分
    
    参数:
        topic_description: 课题的目标、技术路线、人员分工或立项规划说明
        topic_title: 课题名称或代号
        output_path: 可选的 Markdown 输出保存路径 (如 认知/课题战略审查报告.md)
    """
    if not topic_description.strip():
        raise ValueError("课题描述为空，无法进行战略审查。")
    
    messages = [
        {"role": "system", "content": TOPIC_SYSTEM_PROMPT},
        {"role": "user", "content": f"【课题名称】：{topic_title}\n\n【课题背景与规划说明】：\n\n{topic_description}"}
    ]
    
    report = call_deepseek(messages, temperature=0.2, max_tokens=3500)
    
    saved_path = None
    if output_path:
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(report, encoding="utf-8")
        saved_path = str(out_p)
    
    return {
        "topic_title": topic_title,
        "report": report,
        "saved_path": saved_path
    }

def main():
    parser = argparse.ArgumentParser(description="Study-Harness: 课题战略审查与四维打分引擎")
    parser.add_argument("--title", "-t", default="拟研课题", help="课题名称")
    parser.add_argument("--desc", "-d", default="", help="课题详细规划描述文本")
    parser.add_argument("--file", "-f", default="", help="包含课题规划描述的文件路径")
    parser.add_argument("--output", "-o", default="", help="审查报告保存的目标路径 (如 认知/课题战略审查报告.md)")
    
    args = parser.parse_args()
    
    content = args.desc
    if args.file:
        f_p = Path(args.file)
        if not f_p.exists():
            print(f"[错误] 文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)
        content = f_p.read_text(encoding="utf-8")
    
    if not content.strip():
        content = """
课题名称：基于轻量化大语言模型的学术专栏写作与批判性拆书系统研发
目标与计划：
1. 宏观目标：为广大 40-60 岁、初中小学文化的普通读者开发一套平民化、接地气、零脑力压栈的学术研创专栏辅助系统；
2. 团队分工：领导层决定每月必须完成 4 篇专栏交付并考核字数与留存率；一线技术开发负责设计 Python 脚本与 Markdown 目录协议；
3. 技术路线：不追求沉重的分布式底层，而是采用轻量级 Python + 纯文本文件流（资料、笔记、认知、假说、记录）。遇到代码难题时，开发人员可以自主调试工具；
4. 风险控制：目前尚未制定具体的死锁放弃指标，团队打算连续攻坚，直到把功能全部实现为止。
"""
        print("[提示] 未提供课题描述，采用内置示范课题...", file=sys.stderr)

    try:
        res = evaluate_topic(content, topic_title=args.title, output_path=args.output or None)
        print(res["report"])
        if res["saved_path"]:
            print(f"\n[+] 课题审查报告已成功保存至: {res['saved_path']}", file=sys.stderr)
    except Exception as e:
        print(f"[错误] 审查失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
