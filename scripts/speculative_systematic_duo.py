#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
speculative_systematic_duo.py: 推测型与条理型异构双智能体协同器 (Chapter 07 配套)
基于《科学研究的艺术》第十一章推测型（浪漫派/巴斯德）与条理型（古典派/工匠）黄金协同机制（泰勒博士大型研究机构法），
由推测先锋（温度 0.8）负责大胆直觉跳跃开疆拓土，条理法官（温度 0.2）负责冷面求证收尾，解决单兵作战的烂尾与平庸困境。
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

# 浪漫派先锋系统提示词（执行温度 0.8）
SPECULATIVE_PROMPT = """你由《科学研究的艺术》第十一章中的【推测型 / 浪漫派科学家】（以微生物学先驱巴斯德为典范）所驱动。
你的思维特质：
1. 擅长跨越现有事实与局限，全凭敏锐直觉跳跃前行；
2. 脑子极快，点子极多，善于运用 Why（目的性反问）和 How（机理性深挖）进行大胆狂想；
3. 敢于把八竿子打不着的领域进行意象嫁接，擅长从混乱中开辟全新未知大陆。

你的任务：
面对用户提出的研究课题或模糊闪念，你不需要考虑万无一失的证据，也不要受现有常规条条框框的束缚！
请提出 2~3 个最具颠覆性、最大胆出人意料的假说雏形（Sparks），说明这个方向为什么值得放手一搏，以及可能的突破切入点。
请用充满激情、锐利、直击核心的语言输出你的先锋设想草图！"""

# 古典派法官系统提示词（执行温度 0.2）
SYSTEMATIC_PROMPT = """你由《科学研究的艺术》第十一章中的【条理型 / 古典派科学家工匠】所驱动。
你的思维特质：
1. 手里没有铁证绝不多迈半步，像冷面裁判一样步步求证；
2. 工作方法井井有条、一丝不苟，一眼能看穿逻辑漏洞与自嗨幻想；
3. 你的历史使命不是否决创意，而是把浪漫派疯子扔下的冒烟草图，敲打改造成结结实实、能够落地的真家伙（防止变成烂尾楼）。

你的任务：
推测型先锋（Speculative-Agent）刚刚提交了天马行空的狂想草案。
请你立刻全面接管该案卷，戴上老花镜逐条冷峻审查：
1. 【照妖镜排雷】：指出先锋设想中哪些属于违背客观常识的狂热臆想，哪些存在逻辑断裂与致命盲区；
2. 【沙里淘金】：精准挑出其中最有价值、最具实操潜力的核心火星子；
3. 【严密对照与实验工程化】：为最具价值的火种设计一套分阶段、控制单一变量、具备基线对照的严密实验/开发验证方案（Pilot 小规模试点 ➔ 逐步排除）；
4. 【止损铁轨】：划定不可逾越的边界与失败止损线。
请以极度严谨、条理分明、冷峻工匠的口吻输出你的求证裁决书！"""

def collaborate_duo(
    topic_or_spark: str,
    max_rounds: int = 1,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    运行推测型与条理型异构双智能体协同推演
    
    参数:
        topic_or_spark: 待研究的课题靶点、初始灵感或技术难题
        max_rounds: 交互轮次（默认 1 轮完整先锋狂想+工匠收尾）
        output_path: 可选的 Markdown 输出保存路径
    """
    if not topic_or_spark.strip():
        raise ValueError("输入课题为空，无法启动双智能体推演。")
    
    # 第一步：浪漫派先锋发散出击（温度 0.8）
    speculative_messages = [
        {"role": "system", "content": SPECULATIVE_PROMPT},
        {"role": "user", "content": f"【拟探索的研究课题 / 灵感火花】：\n\n{topic_or_spark}\n\n请推测型先锋立刻展开狂想，给出破局假说！"}
    ]
    speculative_output = call_deepseek(speculative_messages, temperature=0.8, max_tokens=2500)
    
    # 第二步：古典派法官冷酷接管与求证工程化（温度 0.2）
    systematic_messages = [
        {"role": "system", "content": SYSTEMATIC_PROMPT},
        {"role": "user", "content": f"【原始研究课题】：\n{topic_or_spark}\n\n【浪漫派先锋（Speculative-Agent）提交的狂想草图】：\n{speculative_output}\n\n请条理派工匠法官立刻接管案卷，进行冷面审查并锻造为可执行的工程方案！"}
    ]
    systematic_output = call_deepseek(systematic_messages, temperature=0.2, max_tokens=3000)
    
    full_report = f"""# 异构双智能体协同推演研创专报

> 理论依据：贝弗里奇《科学研究的艺术》第十一章推测型与条理型黄金协同机制  
> 协同引擎：Study-Harness speculative-systematic-duo (推测先锋 0.8 ➔ 条理法官 0.2)  
> 课题靶点：{topic_or_spark[:60]}...

---

## 阶段一：推测先锋（Speculative-Agent · 浪漫派）直觉突袭
*执行温度：0.8 | 核心使命：直觉跳跃、打破常规、开辟未知假说*

{speculative_output}

---

## 阶段二：条理法官（Systematic-Agent · 古典派）冷面审查与方案锻造
*执行温度：0.2 | 核心使命：排雷去浮、严密对照、工程化收敛防烂尾*

{systematic_output}

---

## 总结：学者决裁备忘录
- **已达成的协同共识**：浪漫派成功突破了常规思维死角，而古典派为天马行空的脑洞焊上了严密对照的物理铁轨；
- **人类学者战略动作**：一线执行人员已拥有清晰的实验 SOP，可即刻启动阶段一极小试点（Pilot）验证。
"""
    
    saved_path = None
    if output_path:
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(full_report, encoding="utf-8")
        saved_path = str(out_p)
    
    return {
        "speculative_output": speculative_output,
        "systematic_output": systematic_output,
        "full_report": full_report,
        "saved_path": saved_path
    }

def main():
    parser = argparse.ArgumentParser(description="Study-Harness: 推测型与条理型异构双智能体协同器")
    parser.add_argument("--topic", "-t", default="", help="待推演的研究课题或灵感文本")
    parser.add_argument("--file", "-f", default="", help="包含课题描述的文件路径")
    parser.add_argument("--output", "-o", default="", help="保存协同报告的文件路径 (如 认知/双智能体推演报告.md)")
    
    args = parser.parse_args()
    
    topic = args.topic
    if args.file:
        f_p = Path(args.file)
        if not f_p.exists():
            print(f"[错误] 指定文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)
        topic = f_p.read_text(encoding="utf-8")
    
    if not topic.strip():
        topic = "如何利用大语言模型自动发现未被主流科学文献充分验证的中医药经典配伍反常规律，并规避幻觉伪证？"
        print(f"[提示] 未输入课题，采用内置示范课题: {topic}", file=sys.stderr)
    
    try:
        res = collaborate_duo(topic, output_path=args.output or None)
        print(res["full_report"])
        if res["saved_path"]:
            print(f"\n[+] 协同推演报告已保存至: {res['saved_path']}", file=sys.stderr)
    except Exception as e:
        print(f"[错误] 推演失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
