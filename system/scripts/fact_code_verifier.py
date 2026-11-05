#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fact_code_verifier.py: 事实与代码求证探索服务核心实现 (MCP fact-code-verifier 配套)
理论依据：五步研创法 Step 2「一手资料与初步探针」与《实践论》实践求证
"""

import os
import sys
import time
import datetime
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent.parent

for p in [CURRENT_DIR, PROJECT_ROOT / "scripts"]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from deepseek_client import call_deepseek

FACT_VERIFIER_SYSTEM_PROMPT = """你由毛泽东《实践论》与《科学研究的艺术》第二章【实验】所武装。
你坚守“没有调查就没有发言权，没有亲身求证就没有真知”的铁律。
对于用户提供的文本事实主张或技术断言，坚决拒绝人云亦云，开展多维度的冷峻事实求证：
1. 【主张拆解与核心待验事实】：提取出最关键的经验断言；
2. 【学术共识与权威信源比对】：该主张是否符合当前公认的基线理论与工程常识？有无被伪造或夸大？
3. 【反例与潜在边界条件】：在哪些极端条件、高压并发或非理想环境下该断言会彻底破产？
4. 【一手实证检验方案建议】：指导学者如何设计一个耗时最短、成本最低的物理/代码测试探针进行当场验伪。

执行温度为 0.2（极致客观求实）。
严格按以下格式输出求证专报：

# 事实与观点实证核验专报：[核验主题]

> 理论依据：五步研创法 Step 2 一手资料探针与《实践论》求证法则  
> 核心心法：绝不道听途说，每一项关键主张必须经过一手实证求证。

## 一、主张断言与核心待验命题
- **待验断言**：...
- **关键经验参数**：...

## 二、学术与工业界共识比对
- **公认基线状态**：...
- **争议焦点/夸大风险**：...

## 三、失效边界与脆弱反例
- **边界条件 1**：...
- **边界条件 2**：...

## 四、低成本一手实证探针建议
[给出 1~2 个最快上手验证真伪的操作步骤]
"""

CODE_VERIFIER_SYSTEM_PROMPT = """你由毛泽东《实践论》与计算机系统工程实证哲学所武装。
用户提供了一段代码探针及其真实的运行终端输出与耗时。
请对其进行冷酷的工程实证分析：
1. 【运行结果真实性与开销审计】：穿透终端输出，客观判定代码是否真实达成了设计意图；
2. 【隐藏死锁与暗坑排查】：指出在真实生产环境或边缘输入下可能爆发的内存泄漏、并发竞争或状态爆炸；
3. 【优化重构与鲁棒探针设计】：给出更高可靠性、更严密的实证探测代码建议。

执行温度为 0.2。
严格按以下格式输出分析：

# 代码探针实证实测专报：[探针主题]

> 理论依据：五步研创法 Step 2 代码探针即时求证  
> 核心心法：Talk is cheap, show me the code and execution trace.

## 一、探针运行实况审计
- **执行状态**：...
- **资源开销与耗时表现**：...

## 二、隐患排查与逻辑死穴
- **潜在风险点**：...

## 三、实证结论与工程建议
- **结论**：...
"""

def verify_claim_or_code(
    claim_or_code: str,
    verification_type: str = "fact",
    topic_name: str = "待求证条目",
    output_file: str = ""
) -> Dict[str, Any]:
    """执行事实或代码探针求证"""
    v_type = verification_type.lower().strip()
    
    if v_type == "code":
        # 运行代码探针并捕获真实终端输出
        exec_output = ""
        exec_error = ""
        duration = 0.0
        success = True
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tf:
            tf.write(claim_or_code)
            temp_script = tf.name
            
        try:
            start_t = time.time()
            proc = subprocess.run(
                [sys.executable, temp_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            duration = time.time() - start_t
            exec_output = proc.stdout.strip()
            exec_error = proc.stderr.strip()
            if proc.returncode != 0:
                success = False
        except subprocess.TimeoutExpired:
            success = False
            exec_error = "探针执行超时 (超过 10 秒上限)"
            duration = 10.0
        except Exception as e:
            success = False
            exec_error = f"探针执行异常: {str(e)}"
        finally:
            if os.path.exists(temp_script):
                os.remove(temp_script)
                
        prompt = (
            f"【待实证代码探针】：\n{claim_or_code.strip()}\n\n"
            f"【探针实测运行结果】：\n"
            f"- 执行状态：{'成功 (0)' if success else '异常退出'}\n"
            f"- 真实执行耗时：{duration:.4f} 秒\n"
            f"- 标准输出 (stdout)：\n{exec_output if exec_output else '（无输出）'}\n"
            f"- 错误输出 (stderr)：\n{exec_error if exec_error else '（无错误）'}\n"
        )
        messages = [
            {"role": "system", "content": CODE_VERIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        report = call_deepseek(messages, temperature=0.2, max_tokens=2500)
    else:
        # 事实核验
        prompt = f"【待核验事实主张或技术断言】：\n主题代号：{topic_name}\n\n主张详情：\n{claim_or_code.strip()}"
        messages = [
            {"role": "system", "content": FACT_VERIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        report = call_deepseek(messages, temperature=0.2, max_tokens=2500)
        
    saved_path = None
    if output_file:
        out_f = Path(output_file)
        if not out_f.is_absolute():
            out_f = PROJECT_ROOT / out_f
        out_f.parent.mkdir(parents=True, exist_ok=True)
        out_f.write_text(report, encoding="utf-8")
        saved_path = str(out_f)
    else:
        # 默认保存至 笔记/YYYY-MM-DD_<topic>.md
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        safe_topic = "".join(c for c in topic_name if c.isalnum() or c in ("-", "_")).strip() or "求证条目"
        notes_dir = PROJECT_ROOT / "笔记"
        notes_dir.mkdir(parents=True, exist_ok=True)
        out_f = notes_dir / f"{today_str}_{safe_topic}_求证笔记.md"
        out_f.write_text(report, encoding="utf-8")
        saved_path = str(out_f)
        
    return {
        "topic": topic_name,
        "type": v_type,
        "report": report,
        "saved_path": saved_path
    }
