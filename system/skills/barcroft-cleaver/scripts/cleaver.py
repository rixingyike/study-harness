#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cleaver.py: 巴克罗夫特极简飞刀与认知提炼引擎核心实现 (SKILL barcroft-cleaver 配套)
理论依据：五步研创法 Step 3「巴克罗夫特极简拆解」与《实践论》理性认知跃迁
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

BARCROFT_SYSTEM_PROMPT = """你由生理学巨匠约瑟夫·巴克罗夫特爵士与毛泽东《矛盾论》《实践论》所武装。
贝弗里奇评价巴克罗夫特：“在面对任何极度复杂、千头万绪的生理机理难题时，巴克罗夫特总是拥有如同快刀斩乱麻般的卓越天才——他毫不留情地把次要变量和枝节干扰全部剥离，只死死揪住那个唯一的、起绝对主导支配作用的决定性因素。”

你的任务是对用户提供的芜杂材料、求证笔记或业务乱局施加“巴克罗夫特极简飞刀”：
1. 【多变量纠缠乱麻透视】：梳理表面上看似都很重要的干扰因素；
2. 【巴克罗夫特极简飞刀裁决】：
   - 绝不搞折中主义的中庸平衡，敢于一刀切除 80% 的枝叶；
   - 旗帜鲜明地提炼出唯一的核心主要矛盾（Single Dominant Factor）；
3. 【底层齿轮因果传动微观拆解】：
   - 证明为什么只要这个主导因素转动，其他次要现象就会身不由己地连锁演变；
4. 【无损认知标签网格式沉淀】：
   - 提取 3~5 个高维认知标签（如 `#主要矛盾/状态爆炸`、`#机理链条/锁竞争`），给出对应索引摘要，便于汇入 `认知/标签.md`。

执行温度为 0.2（极致收敛、洞若观火、一针见血）。
严格按以下格式输出分析专报：

# 巴克罗夫特极简认知专报：[课题/领域代号]

> 理论依据：五步研创法 Step 3 巴克罗夫特极简飞刀与《矛盾论》  
> 核心心法：敢于砍去繁复枝叶，在千头万绪中只揪住唯一的核心主导因素。

## 一、纷繁乱象透视与干扰变量剔除
- **表面纠缠乱象**：...
- **一刀剔除的次要干扰**：...

## 二、巴克罗夫特极简飞刀：唯一核心主导因素
- **主要矛盾定义**：...
- **一票否决权论证**：[论述为何此因素居于支配地位]

## 三、底层因果链条（物理齿轮咬合机制）
[一步步推演主导因素如何撬动全局]

## 四、无损认知标签索引（可并入 认知/标签.md）
- **标签 1**：...
- **标签 2**：...
"""

def apply_barcroft_cleaver(
    notes_or_data: str,
    domain_topic: str = "研究领域",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """运行巴克罗夫特极简飞刀提炼认知"""
    prompt = f"【待拆解的资料/求证笔记要点】：\n领域课题：{domain_topic}\n\n内容详情：\n{notes_or_data.strip()}"
    messages = [
        {"role": "system", "content": BARCROFT_SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    report = call_deepseek(messages, temperature=0.2, max_tokens=2500)
    
    saved_path = None
    tags_path = None
    
    cognition_dir = PROJECT_ROOT / "认知"
    cognition_dir.mkdir(parents=True, exist_ok=True)
    
    if output_path:
        out_f = Path(output_path)
        if not out_f.is_absolute():
            out_f = PROJECT_ROOT / out_f
        out_f.parent.mkdir(parents=True, exist_ok=True)
        out_f.write_text(report, encoding="utf-8")
        saved_path = str(out_f)
    else:
        safe_topic = "".join(c for c in domain_topic if c.isalnum() or c in ("-", "_")).strip() or "极简认知"
        out_f = cognition_dir / f"{safe_topic}_极简认知.md"
        out_f.write_text(report, encoding="utf-8")
        saved_path = str(out_f)
        
    # 维护 认知/标签.md
    tags_file = cognition_dir / "标签.md"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tags_snippet = f"\n\n### [{now_str}] 《{domain_topic}》高维认知标签索引\n"
    if "## 四、无损认知标签索引" in report:
        tags_part = report.split("## 四、无损认知标签索引", 1)[1].strip()
        tags_snippet += f"- 来源专报：`认知/{Path(saved_path).name}`\n{tags_part}\n"
    else:
        tags_snippet += f"- 来源专报：`认知/{Path(saved_path).name}`\n"
        
    if not tags_file.exists():
        header = "# 全局高维认知标签索引网络（认知/标签.md）\n\n> 作用：基于二级标题建立无损标签体系，连接底层原始资料与高维理性认知。\n"
        tags_file.write_text(header + tags_snippet, encoding="utf-8")
    else:
        with tags_file.open("a", encoding="utf-8") as f:
            f.write(tags_snippet)
    tags_path = str(tags_file)
    
    return {
        "topic": domain_topic,
        "report": report,
        "saved_path": saved_path,
        "tags_path": tags_path
    }

def main():
    parser = argparse.ArgumentParser(description="巴克罗夫特极简飞刀与认知提炼引擎 (SKILL barcroft-cleaver)")
    parser.add_argument("--notes", "-n", required=True, help="待拆解提炼的笔记、求证数据或方案细节")
    parser.add_argument("--topic", "-t", default="研究领域", help="领域代号或主题")
    parser.add_argument("--output", "-o", default="", help="极简认知报告输出路径 (默认 认知/<topic>_极简认知.md)")
    
    args = parser.parse_args()
    res = apply_barcroft_cleaver(args.notes, domain_topic=args.topic, output_path=args.output or None)
    print(res["report"])
    print(f"\n[+] 认知专报已归档至: {res['saved_path']}")
    print(f"[+] 标签网络已更新至: {res['tags_path']}")

if __name__ == "__main__":
    main()
