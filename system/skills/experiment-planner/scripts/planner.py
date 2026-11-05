#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planner.py: 实验策划引擎核心实现 (SKILL experiment-planner 配套)
理论依据：贝弗里奇《科学研究的艺术》第二章「实验」之实用主义渐进三步法与对照防骗铁律
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

PLANNER_SYSTEM_PROMPT = """你由百年名著《科学研究的艺术》第二章【实验】武装。
贝弗里奇指出：“实验是检验假说的终极法庭，但也是最善于伪装的骗子。缺乏严格对照的实验不仅毫无价值，甚至会像约翰·亨特把淋病与梅毒混淆那样误导整个学界半个世纪。”
在面对任何科研验证需求时，杜绝一上来就搞大而全的决战式盲目试错，必须严格遵循三大工程铁律：

1. 【渐进三步法分阶段推进】：
   - ① Pilot 极小规模试点：用最低算力/耗材成本试跑极简原型，探测信号窗口并验证链路可行性；
   - ② 大稀释度摸底观测：放大变量跨度，粗粒度定位敏感区间；
   - ③ 大范围精准海选：在已收敛的靶心区间进行高精度统计对照。
2. 【严密对照防骗审查（Control Baseline）】：
   - 必须设计毫无争议的空白对照（Negative Control）与标杆对照（Positive Control）；
   - 彻底审查是否存在未受控隐藏变量（如环境波动、数据泄漏、假阳性伪信号）。
3. 【单一变量与逐步排除法】：
   - 一次只变动一个核心因素，优先设计最关键的决定性实验（Crucial Experiment），用逐步排除法快速压缩候选假说空间。

执行温度为 0.2（冷酷严谨、拒绝浮夸、高度工程化）。
请对用户提供的验证假说或实验需求进行深度策划，严格按以下格式输出实验策划书：

# 渐进式实验策划与对照设计方案：[课题名称]

> 理论依据：贝弗里奇《科学研究的艺术》第二章「实验」  
> 核心原则：Pilot极小试点探路、严守对照防骗铁轨、单一变量逐步排除。

## 一、验证靶心与核心假说提炼
[提炼待检验的核心假设，明确因果关系判断标准]

## 二、三阶段渐进推进路线图
- **阶段 1：Pilot 极小试点方案（最低成本探路）**
  - 规模与配比：...
  - 核心观察指标：...
  - 通过判据与止损线：...
- **阶段 2：大稀释度摸底观测**
  - 变量梯度设计：...
- **阶段 3：大范围精准海选**
  - 统计学显著性要求：...

## 三、对照组防骗设计与变量隔离审查
| 实验组别 | 核心配置/变量操作 | 对照目的 | 规避的伪相关/潜在假阳性 |
| :--- | :--- | :--- | :--- |
| 空白/基线对照组 | ... | ... | ... |
| 阳性/标准对照组 | ... | ... | ... |
| 变量隔离实验组 A | ... | ... | ... |

## 四、逐步排除法与决定性实验排期
[列出第一步最简单、最能一锤定音的判决实验步骤]
"""

def plan_experiment(
    query_or_hypothesis: str,
    topic_name: str = "未命名课题",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """执行实验策划分析"""
    user_prompt = f"【拟检验假说或实验需求】：\n课题代号：{topic_name}\n\n详细说明：\n{query_or_hypothesis.strip()}"
    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    report = call_deepseek(messages, temperature=0.2, max_tokens=2500)
    
    saved_path = None
    if output_path:
        out_file = Path(output_path)
        if not out_file.is_absolute():
            out_file = PROJECT_ROOT / out_file
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(report, encoding="utf-8")
        saved_path = str(out_file)
        
    return {
        "topic": topic_name,
        "report": report,
        "saved_path": saved_path
    }

def main():
    parser = argparse.ArgumentParser(description="实验设计策划引擎 (SKILL experiment-planner)")
    parser.add_argument("--query", "-q", required=True, help="拟验证的假说或实验需求说明")
    parser.add_argument("--topic", "-t", default="科研验证课题", help="课题代号或名称")
    parser.add_argument("--output", "-o", default="", help="策划书保存路径 (如 假说/实验策划书.md)")
    
    args = parser.parse_args()
    res = plan_experiment(args.query, topic_name=args.topic, output_path=args.output or None)
    print(res["report"])
    if res["saved_path"]:
        print(f"\n[+] 实验策划书已成功保存至: {res['saved_path']}", file=sys.stderr)

if __name__ == "__main__":
    main()
