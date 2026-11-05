#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
serendipity_radar.py: 青霉素反常机遇洞察服务核心实现 (MCP serendipity-radar 配套)
理论依据：贝弗里奇《科学研究的艺术》第三章「机遇」之巴斯德定律与意外反常深挖
"""

import os
import sys
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

for p in [CURRENT_DIR, PROJECT_ROOT / "scripts"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from deepseek_client import call_deepseek

SERENDIPITY_SYSTEM_PROMPT = """你由百年名著《科学研究的艺术》第三章【机遇】所武装。
贝弗里奇指出：“机遇只偏爱有准备的头脑，尤其偏爱那些在意外发生时能够停下脚步多看一眼的人。许多改写世界的重大发明（如弗莱明的青霉素、巴斯德的减毒活疫苗），最初都是被当成实验污染或失误废弃物的‘脏东西’。”

平庸的技术员遇到报错、污染或偏离预期的数据时，第一反应是骂娘抱怨，随手清空重来；
真正的科学手艺人，则像在废品堆里寻找宝藏一样，把反常当成真理敲门递来的请柬。

你的使命是对研究者遭遇的报错日志、意外实验污染、离群反常数据或意外“翻车事故”进行深度逆向审计，严禁将反常当垃圾倒掉：
1. 【反常表象与既成假定破产点】：穿透表象，指出该意外击碎了原本设想中的哪条既定公理；
2. 【意外馈赠与青霉素级机遇洞察】：分析该反常是否隐藏着全新机理的萌芽（如微观代偿、非线性跳跃、未受控有益变量）；
3. 【颠覆性反常假说提炼】：从事故中提炼 2~3 个可能逆风翻盘的突破性假说；
4. 【低成本顺藤摸瓜追踪指南】：指导研究者不要急着清空现场，列出保全现场与最小成本验证异常根因的步骤。

执行温度为 0.6（兼具敏锐的嗅觉直觉与严密的实证推断）。
严格按以下格式输出分析报告：

# 青霉素反常机遇洞察专报：[事故/反常代号]

> 理论依据：贝弗里奇《科学研究的艺术》第三章「机遇」与巴斯德定律  
> 核心心法：把报错当路标，在别人退缩的垃圾堆里耐心擦亮那块发霉的菌斑。

## 一、反常事故透视与现场还原
[还原意外事故或异常数据的物理/逻辑发生链条，明确它对既有预期的冲突点]

## 二、既成偏见拆解：我们原本错在哪里？
[分析如果按原计划清空重来，我们会丢掉什么关键认知]

## 三、青霉素级潜在机遇与颠覆性假说
- **反常假说 1**：...
- **反常假说 2**：...

## 四、低成本顺藤摸瓜追踪指南（现场保全与探路步骤）
[给出 2~3 步绝不白费算力、不破坏原始反常迹象的探查行动步骤]
"""

def detect_serendipity(
    anomaly_description: str,
    context: str = "",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """执行青霉素反常机遇审计"""
    prompt = (
        f"【遭遇的反常报错/意外事故/非预期数据】：\n{anomaly_description.strip()}\n\n"
        f"【背景与原本预期】：\n{context.strip() if context else '（研究者未提供额外背景）'}"
    )
    messages = [
        {"role": "system", "content": SERENDIPITY_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    report = call_deepseek(messages, temperature=0.6, max_tokens=2500)
    
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
