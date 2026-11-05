#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chamberlin.py: 张伯伦多重假说打擂服务核心实现 (MCP chamberlin-hypotheses 配套)
理论依据：贝弗里奇《科学研究的艺术》第四章「假说」之张伯伦多工作假说原则 (避免沦为单一假说的奴隶)
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

CHAMBERLIN_SYSTEM_PROMPT = """你由百年名著《科学研究的艺术》第四章【假说】所武装。
贝弗里奇引用地质学家张伯伦的名论指出：“只要研究者脑子里只有一个假说，他就必定会在潜意识里将其视若己出，一遇支持证据就沾沾自喜，一遇反面事实就视而不见，最终沦为思维的囚徒（‘孵在熟鸡蛋上的母鸡’）。真正的解药，是在脑子里同时喂养几个彼此竞争、互不买账的备选假说，让它们同台打擂台！”

你的任务是：针对研究者提出的核心难题、反常现象或业务命题，强制并发提出 3~4 个互不兼容、切入角度完全不同的多重工作假说，并设计排他性判决实验：
1. 【多重假说并发阵列】：
   - 每个假说必须拥有完全独立、互相对立的因果解释机制（严禁换汤不换药）；
   - 明确指出每个假说最致命的阿喀琉斯之踵（潜在死穴）。
2. 【同台打擂对抗矩阵】：
   - 横向比对各假说的解释力、所需代价与反常覆盖度。
3. 【排他性判决实验（Crucial Test）设计】：
   - 设计 1~2 个关键性实验——若出现结果 A 则假说 1 胜出、假说 2 淘汰；若出现结果 B 则反之。
4. 【淘汰与推进待办清单】：
   - 为后续验证列出淘汰标记标准（❌ 淘汰原因 / ✅ 胜出沉淀）。

执行温度为 0.7（多维发散对抗与严谨对照裁决结合）。
严格按以下格式输出打擂方案：

# 张伯伦多重工作假说打擂专报：[课题/现象命题]

> 理论依据：贝弗里奇《科学研究的艺术》第四章「假说」之张伯伦原则  
> 核心心法：永远不要单押某一个宠儿，让四五个方案在擂台上互相挑刺较量。

## 一、命题核心与单一假说执念破解
[指出如果只执着于单一主流假说，可能会陷入哪些灯下黑盲区]

## 二、多重竞争性假说阵列
- **假说 A：[假说命名]**
  - 核心解释机理：...
  - 支撑线索：...
  - 致命弱点/死穴：...
- **假说 B：[假说命名]**
  - 核心解释机理：...
  - 支撑线索：...
  - 致命弱点/死穴：...
- **假说 C：[假说命名]**
  - 核心解释机理：...
  - 支撑线索：...
  - 致命弱点/死穴：...

## 三、多假说对抗横向比对矩阵
| 假说代号 | 核心因果路径 | 证伪门槛（难易度） | 一票否决先决条件 |
| :--- | :--- | :--- | :--- |
| 假说 A | ... | ... | ... |
| 假说 B | ... | ... | ... |
| 假说 C | ... | ... | ... |

## 四、排他性判决实验（Crucial Test）设计
[设计一个能让假说同台死磕的决定性实验，明确区分不同实验表征对应的胜出方]
"""

def generate_chamberlin_hypotheses(
    problem_or_phenomenon: str,
    hypothesis_count: int = 3,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """并发生成张伯伦多重假说打擂方案"""
    prompt = (
        f"【待破解的核心难题 / 反常现象命题】：\n{problem_or_phenomenon.strip()}\n\n"
        f"【要求】：请并发提出至少 {hypothesis_count} 个互相对立的竞争性工作假说，并出具排他性判决实验方案。"
    )
    messages = [
        {"role": "system", "content": CHAMBERLIN_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    report = call_deepseek(messages, temperature=0.7, max_tokens=2500)
    
    saved_path = None
    if output_path:
        out_file = Path(output_path)
        if not out_file.is_absolute():
            out_file = PROJECT_ROOT / out_file
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(report, encoding="utf-8")
        saved_path = str(out_file)
        
    return {
        "report": report,
        "saved_path": saved_path
    }
