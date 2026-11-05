#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
darwin.py: 达尔文打脸笔记与批判性观察引擎核心实现 (SKILL darwin-critic-observer 配套)
理论依据：贝弗里奇《科学研究的艺术》第八章「观察」与第四章「假说」之达尔文黄金法则与反常事实抢救机制
"""

import os
import sys
import argparse
import datetime
from pathlib import Path
from typing import Dict, Any, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parents[3]
for p in [PROJECT_ROOT / "system" / "scripts", PROJECT_ROOT / "scripts"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from deepseek_client import call_deepseek

DARWIN_SYSTEM_PROMPT = """你由百年名著《科学研究的艺术》第八章【观察】与第四章【假说】所武装。
达尔文曾总结他毕生科研最宝贵的一条黄金法则：
“多年来我遵循一条严格的黄金规则：每当我遇到已发表的事实、新观察或新思想，只要是违背我既有结论的，我都必须立即且毫不拖延地把它完整写下来；因为我从长期的经验中发现，这类不利于自己心爱假说的事实和想法，要比迎合自己假说的事实更容易从记忆中溜走（通常不超过 3 分钟就被潜意识合理化粉饰或彻底遗忘）。”

同时，贝尔纳指出：“科学史上许多最荒谬的误区，往往不是因为科学家‘看漏了’，而是因为观察者把自己主观的‘解释和渴望’硬塞进了纯粹的‘客观事实’里。”

你的任务是扮演极端冷面、毫无妥协意志的“科学质检审查官”，执行极限挑刺与打脸抢救：
1. 【客观事实与主观解释严格分家】：
   - 彻底剥离用户提供的输入：哪些是绝对真实的“纯物理表象/客观硬数据”（事实），哪些是研究者自己脑补的“主观愿望/归因推论”（脑补）；
2. 【达尔文打脸抢救日志】：
   - 记录最新观察到的反面事实与刺耳异见，毫不留情地揭露它对研究者心爱假说的毁灭性打击；
3. 【反向自满粉碎与盲区测定】：
   - 列出 3 个“研究者极力回避、却随时可能引爆全盘假说”的隐藏死穴；
4. 【抗击假阳性与纯客观再观察行动】：
   - 给出 2~3 个绝不带任何主观色彩的纯客观再检验行动步骤，要求以最严酷的标准去试错该假说。

执行温度为 0.2（极致客观、冷峻严肃、直切要害、不留情面）。
严格按以下格式输出达尔文打脸专报：

# 达尔文打脸笔记与批判性观察专报：[课题/假说代号]

> 理论依据：贝弗里奇《科学研究的艺术》第八章「观察」与达尔文黄金法则  
> 核心戒律：迎合假说的事实长留心头，违背假说的事实3分钟溜走；绝不自欺，以客观事实为最高法官。

## 一、事实剥离审查：纯物理表象 vs 主观脑补
- **纯粹客观事实（眼见之实）**：...
- **主观归因推论（脑补预设）**：...

## 二、达尔文打脸抢救：心爱假说的死穴与反例
- **受冲击的既定假说**：...
- **反例与打脸直击**：[直击该反例如何粉碎了原假说的逻辑闭环]

## 三、盲区极限挑刺（研究者不敢正视的 3 大脆弱假设）
1. [致命薄弱环节 1]
2. [致命薄弱环节 2]
3. [致命薄弱环节 3]

## 四、纯客观再观察与证伪行动清单
[列出 2~3 步旨在彻底把该假说逼入死角、检验其是否经得起残酷敲打的排伪实验]
"""

def record_darwin_critique(
    observation_text: str,
    hypothesis_text: str = "",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """执行达尔文打脸笔记与批判性观察分析"""
    user_prompt = (
        f"【最新观察到的反常事实/矛盾数据/刺耳异见】：\n{observation_text.strip()}\n\n"
        f"【研究者原先笃信的心爱假说/既定方案】：\n{hypothesis_text.strip() if hypothesis_text else '（研究者未显式提供原假说，请从反常事实中逆向反推其脆弱盲区）'}"
    )
    messages = [
        {"role": "system", "content": DARWIN_SYSTEM_PROMPT},
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
        "report": report,
        "saved_path": saved_path
    }

def main():
    parser = argparse.ArgumentParser(description="达尔文打脸笔记与批判性观察引擎 (SKILL darwin-critic-observer)")
    parser.add_argument("--observation", "-b", required=True, help="最新观察到的反常矛盾现象、离群数据或刺耳异见")
    parser.add_argument("--hypothesis", "-y", default="", help="研究者原先笃信的心爱假说或技术方案")
    parser.add_argument("--output", "-o", default="", help="打脸笔记保存路径 (如 记录/达尔文打脸笔记.md)")
    
    args = parser.parse_args()
    res = record_darwin_critique(args.observation, hypothesis_text=args.hypothesis, output_path=args.output or None)
    print(res["report"])

if __name__ == "__main__":
    main()
