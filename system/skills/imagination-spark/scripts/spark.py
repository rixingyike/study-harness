#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spark.py: 想象力激发引擎核心实现 (SKILL imagination-spark 配套)
理论依据：贝弗里奇《科学研究的艺术》第五章「想象力」之 Why & How 提问手艺
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

SPARK_SYSTEM_PROMPT = """你由百年名著《科学研究的艺术》第五章【想象力】所武装。
贝弗里奇指出：“假说的大胆提出依赖于活跃的想象力，而想象力往往由恰当的提问所点燃。”
在面对任何科研资料、反常现象或卡壳难题时，杜绝死记硬背与机械苦熬，必须运行 Why & How 双螺旋提问手艺：

1. 【追问“为什么（Why）”——目的性与宏观跨界突破】：
   - 为什么这个现象偏偏在这时发生？为什么现有的公认解释行不通？
   - 逼迫思维跨越现有边界，将两个八竿子打不着的领域进行意象嫁接，激发颠覆性假说。
2. 【追问“怎么样（How）”——微观机理与物理咬合齿轮】：
   - 这到底是怎么一步步演变的？微观上的物理/化学/逻辑齿轮是如何咬合传动的？
   - 像约翰·亨特因见鹿角结扎血管意外发现侧支循环一样，盯死每一个反常细节的物理发生链条。

执行温度为 0.8（发散联想、大胆跨界、打破常规定势）。
请对用户提供的资料片段或难题进行深度穿透，严格按以下格式输出分析报告：

# 想象力激发与 Why & How 双螺旋分析报告：[主题名称]

> 理论依据：贝弗里奇《科学研究的艺术》第五章「想象力」  
> 核心心法：以 Why 打破边界，以 How 咬死微观机理，在松弛与好奇中点燃灵感火花。

## 一、现象透视与常规假定破解
[简要剖析现象表象，指出人们往往在哪些理所当然的“常规假定”里陷入了思维死锁]

## 二、Why 维度：目的性与跨界反问（3 大颠覆性假设火花）
- **火花 1**：...
- **火花 2**：...
- **火花 3**：...

## 三、How 维度：微观机理齿轮拆解
[深入底层物理/逻辑发生链条，列出 2~3 个具体咬合环节的推演细节]

## 四、下一步建议探索切入点
[给出 1~2 个最值得放手一试的最小验证切入点]
"""

def spark_imagination(
    query_or_text: str,
    topic_name: str = "未命名课题",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    运行 Why & How 提问手艺，激发想象力与跨界破局假说 (温度 0.8)
    """
    user_prompt = f"【待分析课题或资料片段】：\n课题名称：{topic_name}\n\n内容描述：\n{query_or_text}"
    
    messages = [
        {"role": "system", "content": SPARK_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    report = call_deepseek(messages, temperature=0.8, max_tokens=2200)
    
    saved_path = ""
    if output_path:
        out_p = Path(output_path)
        if not out_p.is_absolute():
            out_p = PROJECT_ROOT / out_p
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(report, encoding="utf-8")
        saved_path = str(out_p)
        
    return {
        "topic_name": topic_name,
        "report": report,
        "saved_path": saved_path
    }

def main():
    parser = argparse.ArgumentParser(description="Study-Harness: 想象力激发引擎 (Why & How)")
    parser.add_argument("--name", "-n", default="科研难题", help="课题或问题名称")
    parser.add_argument("--text", "-t", default="", help="问题或资料文本")
    parser.add_argument("--output", "-o", default="", help="输出 Markdown 文件路径")
    args = parser.parse_args()

    content = args.text
    if not content.strip():
        content = "大模型在单函数生成时准确率高，但在跨文件长上下文修改时频繁出现幻觉与接口错位。"
    
    res = spark_imagination(content, topic_name=args.name, output_path=args.output or None)
    print(res["report"])

if __name__ == "__main__":
    main()
