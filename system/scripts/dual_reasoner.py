#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual_reasoner.py: 侦探与法官双智能体推演引擎核心实现 (MCP dual-agent-reasoning 配套)
理论依据：贝弗里奇《科学研究的艺术》第七章「推理」之侦探与法官职能严格分离
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

for p in [CURRENT_DIR, PROJECT_ROOT / "scripts"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from deepseek_client import call_deepseek

DETECTIVE_PROMPT = """你由百年名著《科学研究的艺术》第七章【推理】中的【敏锐侦探】角色驱动。
在贝弗里奇的科学方法论中：“大模型与学者最擅长推理，但在推演中必须严格拆分两种职能角色：侦探负责由表及里的大胆假设，法官负责滴水不漏的逻辑核验。”

你的思维特质（执行温度 0.8）：
1. 擅长从最微弱、模糊、反常的线索中寻找不为人知的关联；
2. 不拘泥于现成公理或刻板规矩，敢于提出出人意料的因果分支与假说雏形；
3. 大胆猜测背后的真实动因、物理机制或潜在漏洞。

请针对用户提供的线索与前提，提出 2~3 个最具洞察力与突破张力的侦探假说（Sparks）。语言敏锐、充满悬念与穿透力。"""

JUDGE_PROMPT = """你由百年名著《科学研究的艺术》第七章【推理】中的【冷面法官】角色驱动。
在贝弗里奇的科学方法论中：“法官手握既定公理与铁证，必须对侦探的一切直觉联想进行最严苛的逻辑闭环审查，杜绝自嗨臆断与伪科学。”

你的思维特质（执行温度 0.2）：
1. 极度冷面、客观、严谨，手里没有铁证绝不认定因果链条；
2. 逐条审查侦探提交的假设：挑出其中的常识漏洞、证据断裂与无根据臆测；
3. 挑选出最具验证可能的核心假说，为其设计严密的排查与逻辑闭环验证步骤（排除法、对照组、关键反例测试）；
4. 输出最终具备法律判决般严密性的裁决书。"""

def dual_agent_reason(
    clue_or_premise: str,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    运行侦探与法官双智能体推演 (侦探 0.8 ➔ 法官 0.2)
    """
    # 阶段一：侦探直觉追踪
    detective_res = call_deepseek([
        {"role": "system", "content": DETECTIVE_PROMPT},
        {"role": "user", "content": f"【案件线索 / 课题前提】：\n{clue_or_premise}\n\n请提出你的敏锐侦探推测与假说分支："}
    ], temperature=0.8, max_tokens=1800)
    
    # 阶段二：法官冷面核验与闭环裁决
    judge_input = (
        f"【原始线索与前提】：\n{clue_or_premise}\n\n"
        f"【侦探推测卷宗】：\n{detective_res}\n\n"
        f"请法官全面接管卷宗，进行逻辑排查、排伪核验并给出终局闭环裁决书："
    )
    judge_res = call_deepseek([
        {"role": "system", "content": JUDGE_PROMPT},
        {"role": "user", "content": judge_input}
    ], temperature=0.2, max_tokens=2200)
    
    full_report = f"""# 侦探与法官双智能体推理推演报告

> 理论依据：贝弗里奇《科学研究的艺术》第七章「推理」之侦探与法官职能分离  
> 推演流程：侦探先锋（温度 0.8 直觉追踪）➔ 法官审判（温度 0.2 冷面排伪闭环）

---

## 阶段一：【敏锐侦探】线索追踪与假说卷宗（温度 0.8）

{detective_res}

---

## 阶段二：【冷面法官】逻辑核验与闭环裁决书（温度 0.2）

{judge_res}
"""
    
    saved_path = ""
    if output_path:
        out_p = Path(output_path)
        if not out_p.is_absolute():
            out_p = PROJECT_ROOT / out_p
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(full_report, encoding="utf-8")
        saved_path = str(out_p)
        
    return {
        "detective_report": detective_res,
        "judge_report": judge_res,
        "full_report": full_report,
        "saved_path": saved_path
    }
