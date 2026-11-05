#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reader.py: 批判性文献拆解与认知缺陷扫描引擎核心实现 (SKILL critical-reader 配套)
理论依据：五步研创法 Step 1「批判性文献审阅」与《实践论》感性认知输入
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

CRITICAL_SYSTEM_PROMPT = """你由《科学研究的艺术》第一章【准备】与毛泽东《实践论》所武装。
贝弗里奇指出：“不加批判地阅读，不仅不能启发思想，反而会使心灵沦为他人思想的俘虏。卓越的科学手艺人在阅读时，眼里看到的不是作者宣布了什么，而是作者遗漏了什么、掩盖了什么、在哪些地方前言不搭后语。”

你的任务是对用户提供的文献片段、专著章节或立项材料展开冷峻的批判性审阅：
1. 【核心论点与潜意识前提剥离】：
   - 提取作者最想论证的核心主张；
   - 揪出作者未加证明就视为理所当然的 1~2 个底层前提假定。
2. 【知识空白（Knowledge Gap）极限探查】：
   - 指出材料在机理闭环、适用边界或极端工况下的重大盲区；
   - 哪些环节作者只是含糊其辞一笔带过？
3. 【内在矛盾与观点冲突（Contradictions）】：
   - 指出材料内部逻辑互搏或与成熟工程/物理事实不相容的硬伤漏洞；
4. 【逆向突破靶心与未解之谜提炼】：
   - 提炼 2~3 个最具有颠覆价值的未解靶点，直接作为后续张伯伦假说打擂的精准射击目标。

执行温度为 0.2（极致客观、冷峻挑刺、不迎合吹捧）。
严格按以下格式输出批判审阅专报：

# 批判性文献审阅专报：[文献/课题名称]

> 理论依据：五步研创法 Step 1 与毛泽东《实践论》感性认识阶段  
> 核心戒律：拒绝表面摘要，深挖知识空白与内在矛盾，把不完美变成突破靶心。

## 一、核心论点与底层前提审查
- **核心主张**：...
- **未证明的底层假定**：...

## 二、知识空白（Knowledge Gap）扫描
- **盲区 1**：...
- **盲区 2**：...

## 三、内在矛盾与观点互搏（Contradictions）
- **逻辑硬伤/现实冲突**：...

## 四、逆向突破靶心清单（为假说打擂提供子弹）
1. [未解靶点 1]
2. [未解靶点 2]
"""

def analyze_critical_reading(
    text: str,
    title: str = "参考资料",
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """执行批判性文献审阅分析并自动更新不完美清单"""
    prompt = f"【待审阅文献/资料片段】：\n文献代号：{title}\n\n内容详情：\n{text.strip()}"
    messages = [
        {"role": "system", "content": CRITICAL_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    report = call_deepseek(messages, temperature=0.2, max_tokens=2500)
    
    saved_doc_path = None
    flaws_path = None
    
    target_dir = Path(output_dir) if output_dir else PROJECT_ROOT / "资料"
    if not target_dir.is_absolute():
        target_dir = PROJECT_ROOT / target_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存该文献的单独批判审阅报告
    safe_title = "".join(c for c in title if c.isalnum() or c in ("-", "_", " ")).strip() or "文献"
    doc_file = target_dir / f"{safe_title}_批判审阅.md"
    doc_file.write_text(report, encoding="utf-8")
    saved_doc_path = str(doc_file)
    
    # 自动追加更新 资料/不完美.md
    flaws_file = target_dir / "不完美.md"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    snippet = f"\n\n### [{now_str}] 来源文献：《{title}》漏洞与空白扫描\n"
    # 提取第四部分的靶心内容
    if "## 四、逆向突破靶心清单" in report:
        target_part = report.split("## 四、逆向突破靶心清单", 1)[1].strip()
        snippet += f"{target_part}\n"
    else:
        snippet += f"- 详见批判审阅专报：`资料/{doc_file.name}`\n"
        
    if not flaws_file.exists():
        header = "# 研创资料未解空白与矛盾缺陷汇总库（资料/不完美.md）\n\n> 作用：收录所有经由 critical-reader 审阅提取的未解空白、争议与漏洞，作为假说打擂的直接靶心。\n"
        flaws_file.write_text(header + snippet, encoding="utf-8")
    else:
        with flaws_file.open("a", encoding="utf-8") as f:
            f.write(snippet)
    flaws_path = str(flaws_file)
    
    return {
        "title": title,
        "report": report,
        "saved_report": saved_doc_path,
        "flaws_path": flaws_path
    }

def main():
    parser = argparse.ArgumentParser(description="批判性文献拆解与认知缺陷扫描引擎 (SKILL critical-reader)")
    parser.add_argument("--text", "-t", required=True, help="待审阅文献文本、论文段落或方案内容")
    parser.add_argument("--title", "-n", default="参考资料", help="文献标题或代号")
    parser.add_argument("--output-dir", "-o", default="", help="资料输出目录，默认 资料/")
    
    args = parser.parse_args()
    res = analyze_critical_reading(args.text, title=args.title, output_dir=args.output_dir or None)
    print(res["report"])
    print(f"\n[+] 审阅专报已归档至: {res['saved_report']}")
    print(f"[+] 不完美清单已更新至: {res['flaws_path']}")

if __name__ == "__main__":
    main()
