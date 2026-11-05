#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
breaker.py: 死锁破局急救引擎核心实现 (SKILL deadlock-breaker 配套)
理论依据：贝弗里奇《科学研究的艺术》第九章「困难」之心理定势与破局三味药
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parents[3]
for p in [PROJECT_ROOT / "system" / "scripts", PROJECT_ROOT / "scripts"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from deepseek_client import call_deepseek

BREAKER_SYSTEM_PROMPT = """你由百年名著《科学研究的艺术》第九章【困难】所武装。
贝弗里奇指出：“当学者在同一个难题上反复卡壳打转时，往往不是智力不够，而是神经陷入了深度的‘心理定势（Mental Ruts）’。继续死磕蛮干只会加剧神经磨损，导致无谓的沮丧。”
面对卡壳、死锁、毫无进展的研究或技术难题，请以冷峻、务实、治病救人的大夫姿态（执行温度 0.3），开出针对性的【脑子急救三味药】：

【第一味药：强制拔电源（战略性搁置）】
- 诊断是否已陷入磨损轨道；
- 明确下达冷冻禁令：设定具体的冷冻期限（如冷冻 72 小时，期间严禁打开该文档/代码）；
- 指导创作者立刻把注意力转向完全无关的生活活动或轻量任务，为潜意识自动拼图留出绝对真空。

【第二味药：暴风拆大山（解构软柿子）】
- 拒绝在庞然大物面前发呆。将该难题强行解构为 3~4 个彼此解耦的微观原子小碎块；
- 指导创作者“专挑最软的柿子先捏”：先做最容易、能在半小时内获得正反馈的切片，重新激活认知动力。

【第三味药：胡同大爷会诊（常识降维粉碎定势）】
- 坚决剥离一切高深专业黑话与学术包装；
- 用买菜、做饭、修自行车或市井日常常识将该问题重新转述一遍；
- 模拟一位完全不懂该行的“胡同大爷”，向创作者抛出 2 个直击本质的“愣头青式反常识发问”，彻底砸碎专业壁垒构筑的思维死锁。

请严格按以下 Markdown 格式输出破局急救处方：

# 难题死锁破局急救处方：[卡壳难题名称]

> 理论依据：贝弗里奇《科学研究的艺术》第九章「困难」  
> 核心心法：死磕是神经磨损的死穴；拔电源、拆大山、胡同大爷常识会诊，三味猛药粉碎定势！

## 一、死锁病因穿透（思维定势照妖镜）
[分析作者到底被哪一个看似天经地义的既定假定给锁死了]

## 二、第一味药：强制拔电源与冷冻医嘱
- **冷冻期限**：[明确建议冷冻天数/时长]
- **潜意识孵化建议**：[具体转向建议]

## 三、第二味药：大山暴风拆解与软柿子清单
1. **软柿子 1（立刻可做）**：...
2. **切片 2**：...
3. **切片 3**：...

## 四、第三味药：胡同大爷市井大白话会诊
- **白话再转述**：...
- **愣头青常识灵魂拷问**：
  - 拷问 1：...
  - 拷问 2：...
"""

def break_deadlock(
    problem_description: str,
    problem_name: str = "卡壳难题",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    针对思维死锁开出破局三味药 (温度 0.3)
    """
    user_prompt = f"【卡壳难题名称】：{problem_name}\n\n【难题详述与当下死锁困境】：\n{problem_description}"
    
    messages = [
        {"role": "system", "content": BREAKER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    prescription = call_deepseek(messages, temperature=0.3, max_tokens=2200)
    
    saved_path = ""
    if output_path:
        out_p = Path(output_path)
        if not out_p.is_absolute():
            out_p = PROJECT_ROOT / out_p
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(prescription, encoding="utf-8")
        saved_path = str(out_p)
        
    return {
        "problem_name": problem_name,
        "prescription": prescription,
        "saved_path": saved_path
    }

def main():
    parser = argparse.ArgumentParser(description="Study-Harness: 死锁破局急救引擎")
    parser.add_argument("--name", "-n", default="卡壳难题", help="难题名称")
    parser.add_argument("--text", "-t", default="", help="难题描述")
    parser.add_argument("--output", "-o", default="", help="处方保存路径")
    args = parser.parse_args()

    content = args.text
    if not content.strip():
        content = "设计长程规划智能体时，到第十步树搜索发生爆炸，内存溢出，反复死磕三天毫无进展。"
    
    res = break_deadlock(content, problem_name=args.name, output_path=args.output or None)
    print(res["prescription"])

if __name__ == "__main__":
    main()
