#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
profiler.py: 科学家性格画像与潜能诊断引擎核心实现 (SKILL scientist-profiler 配套)
理论依据：贝弗里奇《科学研究的艺术》第十一章「科学家」
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# 将 system/scripts 加入路径以导入通用客户端
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parents[3]
for p in [PROJECT_ROOT / "system" / "scripts", PROJECT_ROOT / "scripts"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from deepseek_client import call_deepseek

SYSTEM_PROMPT = """你是一位深谙百年科技史与科研心理学的资深战略导师。你的理论体系完全基于剑桥大学老教授 W.I.B. 贝弗里奇的经典名著《科学研究的艺术》第十一章《科学家》。

在贝弗里奇的体系中，世界上几乎没有十全十美的科学家，甚至真正的科技开拓者往往带有反传统的“叛逆与偏执”。
请你保持极致的冷峻、客观与严谨（执行温度 0.2，坚决杜绝廉价的阿谀奉承或励志套话），根据用户提供的学者工作经历、自述、习惯或科研笔记，从以下四大核心维度进行深度画像与量化诊断：

【维度一：反应型 vs 被动型人格诊断（开拓者原生土壤）】
- 反应型（Reactive）：对外界刺激和他人观点起强烈反应，从小怀疑既有现成道理，对教条有叛逆心，往往脾气古怪、不易被世俗规训，具有浓厚的开拓者心性；
- 被动型（Passive）：善于顺从接受正规教育，长于被动积累知识，容易适应生活但在研究上充满成见与公认观点（典型的“应试考霸”，不适合开辟未知疆界）。

【维度二：爱因斯坦科研驱动力三分法】
1. 竞技场运动员：把科学当作施展个人卓越智力、寻找解谜快感的竞技场；
2. 谋生工作者：把科学视作一份谋求体面生活与职业晋升的工具；
3. 真正的献身者：人数极少，视探求真理为不可抗拒的内在神圣召唤，具有近乎痴狂的献身精神。

【维度三：敢于“出洋相”的心理承受力与顽强坚持指数】
- 弗莱克斯纳之问：“你准备好在研究所里当众出洋相了吗？”——能否顶住被权威嘲笑、被同行视作异想天开或狂妄无知的心理压力（如乡村医生詹纳做牛痘接种前害怕丢脸的挣扎）；
- 面对反复挫折与长期没有正反馈时，是否具备达尔文和巴斯德式的“近乎顽强的坚持精神”。

【维度四：科学头脑认知谱系定位（推测型 vs 条理型）】
- 推测型 / 浪漫派（Speculative/Romantic）：凭直觉跳跃前行，早饭还没吃完脑子里已经冒出三个狂想，擅长开辟新领域，但容易粗糙肤浅、留下烂尾楼（如巴斯德）；
- 条理型 / 古典派（Systematic/Classical）：没有铁证绝不多迈半步，工作方法井井有条、像冷面裁判步步求证，善于把发现臻于完善，但缺乏从零到一的破局冲击力。

【输出规范格式】：
请严格按以下 Markdown 格式输出诊断报告：

# 学者性格画像与潜能诊断报告：[学者姓名/标识]

> 理论依据：贝弗里奇《科学研究的艺术》第十一章「科学家」  
> 诊断引擎：Study-Harness scientist-profiler (执行温度 0.2 纯客观收敛)

## 一、 综合诊断概览与定位雷达
- **人格类型判据**：[反应型开拓者 / 被动型知识积累者 / 混合过渡型]（置信度：X%）
- **内在驱动属性**：[竞技场竞技型 / 职业谋生型 / 真正献身型]
- **认知谱系归属**：推测型（浪漫派） X% vs 条理型（古典派） Y%
- **出洋相心理韧性评级**：[高韧性敢为天下先 / 中度体面敏感 / 极度爱惜羽毛防卫型]

## 二、 四维深度剖析与证据链
### 1. 反应型 vs 被动型人格判据（开拓者心性）
[详细引述用户材料，分析其面对权威理论、既有规范与未知问题时的本能反应机制]

### 2. 爱因斯坦科研驱动力本质解析（竞技场 / 谋生 / 真正献身）
[分析其在科研与创作中最能获得持续快感的源动力来源]

### 3. “出洋相”心理耐受与抗挫底线（弗莱克斯纳之问）
[指出其面对外界质疑、同行嗤笑及试错冷眼时的承压阈值与脆弱点]

### 4. 浪漫派先锋 vs 古典派工匠特质对比（推测型 vs 条理型）
[指出其在提出点子、推进求证、收尾交付中的真实长板与致命盲区]

## 三、 专属数字外骨骼（Study-Harness）装配策略
针对该学者的特质，给出具体的系统协作方案：
1. **智能体搭班子建议**：[例如：推测型学者应强制挂载条理型 Systematic-Agent 作为冷面法官；条理型学者应挂载推测型 Speculative-Agent 激发火花]；
2. **防自毁与防烂尾安全阀**：[指出如何通过 SOP 约束其致命短板]；
3. **日常环境与心流保护原则**：[基于贝弗里奇原则，建议其如何安排自由时间、避免朝九晚五式的碎化干扰]。
"""

def profile_scientist(
    profile_text: str,
    scholar_name: str = "研创学者",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """运行科学家性格画像与潜能诊断"""
    if not profile_text.strip():
        raise ValueError("输入内容为空，无法进行性格诊断。")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"【学者姓名/标识】：{scholar_name}\n\n【学者背景材料与工作自述】：\n\n{profile_text}"}
    ]
    
    report = call_deepseek(messages, temperature=0.2, max_tokens=3500)
    
    saved_path = None
    if output_path:
        out_p = Path(output_path).resolve()
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(report, encoding="utf-8")
        saved_path = str(out_p)
    
    return {
        "scholar_name": scholar_name,
        "report": report,
        "saved_path": saved_path
    }

def main():
    parser = argparse.ArgumentParser(description="Study-Harness: 科学家性格画像与潜能诊断引擎")
    parser.add_argument("--name", "-n", default="研创学者", help="学者姓名或标识")
    parser.add_argument("--text", "-t", default="", help="学者的自述、背景或科研习惯文本")
    parser.add_argument("--file", "-f", default="", help="读取包含自述文本的文件路径")
    parser.add_argument("--output", "-o", default="", help="诊断报告保存的目标文件路径")
    
    args = parser.parse_args()
    content = args.text
    if args.file:
        f_path = Path(args.file)
        if not f_path.exists():
            print(f"[错误] 指定文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)
        content = f_path.read_text(encoding="utf-8")
    
    if not content.strip():
        content = """
我平时在单位做技术研发与算法研究。我特别反感领导每天要我们填详细的日报周报和进度表，我觉得真正的突破不是按部就班算出来的。
大学的时候我就不是考高分的学生，考试卷子上的标准答案我总觉得逻辑有漏洞，经常因为跟老师辩论被扣卷面分。
我的桌面永远乱七八糟，堆满了各种半途而废的草稿本和原型代码，我脑子里总有源源不断的新想法，经常散步或者洗澡时蹦出灵感，
恨不得马上搞个大原型。但是我最大的毛病是容易喜新厌旧，一个课题做到70%把核心难点摸通了，我就觉得后面繁琐的打磨测试太枯燥，
容易把摊子扔在那儿开新坑。
另外，我心里其实挺想做出别人没做过的东西，但有时候又有点害怕同行笑话我的点子太幼稚不合常规。
"""
        print("[提示] 未提供输入文本，正在运行内置示范自述...", file=sys.stderr)

    try:
        res = profile_scientist(content, scholar_name=args.name, output_path=args.output or None)
        print(res["report"])
        if res["saved_path"]:
            print(f"\n[+] 诊断报告已成功保存至: {res['saved_path']}", file=sys.stderr)
    except Exception as e:
        print(f"[错误] 诊断失败: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
