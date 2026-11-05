#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chapter_10.py: 专栏第 10 讲配套 SKILL 与 MCP 自动化集成测试套件
验证:
1. 批判性文献审阅技能 (SKILL critical-reader) 规范与执行 (含 资料/不完美.md 自动更新)
2. 事实与代码求证探索服务 (MCP 工具 verify_fact_or_code - 事实核验与代码实测双模式)
3. 巴克罗夫特极简飞刀技能 (SKILL barcroft-cleaver) 规范与执行 (含 认知/标签.md 自动维护)
4. 五步研创流水线总控服务 (MCP 工具 inspect_study_pipeline)
5. MCP Server (mcp_server.py) 第 10 讲工具挂载完整性
"""

import os
import sys
import unittest
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "system" / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "system" / "scripts"))

from deepseek_client import get_api_key
import mcp_server

class TestChapter10Suite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        api_key = get_api_key()
        if not api_key:
            raise unittest.SkipTest("未配置有效的 DEEPSEEK_API_KEY，跳过在线大模型测试。")
        print(f"\n[+] 正在启动第 10 讲集成测试，API Key: {api_key[:6]}...")

    def test_01_critical_reader_skill(self):
        """测试 1: 批判性文献审阅技能 (SKILL critical-reader) 规范与执行"""
        skill_file = PROJECT_ROOT / "system" / "skills" / "critical-reader" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "critical-reader SKILL.md 不存在")
        self.assertIn("name: critical-reader", skill_file.read_text(encoding="utf-8"))

        script_path = PROJECT_ROOT / "system" / "skills" / "critical-reader" / "scripts" / "reader.py"
        spec = importlib.util.spec_from_file_location("reader", script_path)
        reader_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader_mod)

        test_text = (
            "某论文提出：只需增加 Transformer 的层数与隐藏层维度，模型便能自主涌现出具备绝对因果推理能力的强人工智能，"
            "且完全无需外部知识库介入或任何可解释性约束。"
        )
        test_out_dir = PROJECT_ROOT / "tests" / "test_docs"
        res = reader_mod.analyze_critical_reading(test_text, title="尺度律因果论论文", output_dir=str(test_out_dir))

        self.assertIn("批判性文献审阅专报", res["report"])
        self.assertIn("知识空白", res["report"])
        self.assertIn("内在矛盾", res["report"])
        self.assertTrue(Path(res["saved_report"]).exists())
        self.assertTrue(Path(res["flaws_path"]).exists())
        
        # 清理测试产生的临时文档目录
        Path(res["saved_report"]).unlink(missing_ok=True)
        Path(res["flaws_path"]).unlink(missing_ok=True)
        if test_out_dir.exists():
            test_out_dir.rmdir()
        print("  [✓] 批判性文献审阅技能 (SKILL critical-reader) 测试通过")

    def test_02_verify_fact_or_code_mcp(self):
        """测试 2: 事实与代码求证探索 MCP 服务 (verify_fact_or_code)"""
        # A: 事实求证测试
        claim = "Python 中只要使用多线程 (threading.Thread) 就能在多核 CPU 上实现计算密集型任务的真并行加速。"
        test_out_fact = PROJECT_ROOT / "tests" / "output_test_verify_fact.md"
        res_fact = mcp_server.verify_fact_or_code(claim, verification_type="fact", topic_name="GIL多线程并行假说", output_file=str(test_out_fact))
        self.assertIn("事实与观点实证核验专报", res_fact)
        self.assertIn("公认基线", res_fact)
        self.assertTrue(test_out_fact.exists())
        test_out_fact.unlink()

        # B: 代码探针运行实测
        code_probe = """
import time
start = time.time()
res = sum(i * i for i in range(100000))
print(f"CALC_DONE: {res}")
"""
        test_out_code = PROJECT_ROOT / "tests" / "output_test_verify_code.md"
        res_code = mcp_server.verify_fact_or_code(code_probe, verification_type="code", topic_name="简单求和算力探针", output_file=str(test_out_code))
        self.assertIn("代码探针实证实测专报", res_code)
        self.assertIn("CALC_DONE", res_code)
        self.assertTrue(test_out_code.exists())
        test_out_code.unlink()
        print("  [✓] 事实与代码求证探索 MCP 服务 (fact-code-verifier) 测试通过")

    def test_03_barcroft_cleaver_skill(self):
        """测试 3: 巴克罗夫特极简飞刀技能 (SKILL barcroft-cleaver) 规范与执行"""
        skill_file = PROJECT_ROOT / "system" / "skills" / "barcroft-cleaver" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "barcroft-cleaver SKILL.md 不存在")
        self.assertIn("name: barcroft-cleaver", skill_file.read_text(encoding="utf-8"))

        script_path = PROJECT_ROOT / "system" / "skills" / "barcroft-cleaver" / "scripts" / "cleaver.py"
        spec = importlib.util.spec_from_file_location("cleaver", script_path)
        cleaver_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cleaver_mod)

        notes = (
            "经过一手排查：大模型在长程任务中性能下降，团队有人怀疑是温度设置不合理，"
            "有人怀疑是 Token 长度不够，有人怀疑是 Prompt 提示词没有对齐，"
            "但实际硬件监控显示：根本原因在于上下文跨多轮时缺乏工作记忆缓存卸载机制，导致每次都重新全量推理引起注意力状态空间爆炸。"
        )
        test_out = PROJECT_ROOT / "tests" / "output_test_cleaver.md"
        res = cleaver_mod.apply_barcroft_cleaver(notes, domain_topic="长程状态爆炸主导因", output_path=str(test_out))

        self.assertIn("巴克罗夫特极简认知专报", res["report"])
        self.assertIn("主要矛盾", res["report"])
        self.assertTrue(test_out.exists())
        test_out.unlink()
        print("  [✓] 巴克罗夫特极简飞刀技能 (SKILL barcroft-cleaver) 测试通过")

    def test_04_inspect_study_pipeline_mcp(self):
        """测试 4: 五步研创流水线总控 MCP 服务 (inspect_study_pipeline)"""
        res_text = mcp_server.inspect_study_pipeline()
        self.assertIn("五步研创流水线健康度与推进诊断专报", res_text)
        self.assertIn("五大目录流转状态矩阵", res_text)
        self.assertIn("行动指南", res_text)
        print("  [✓] 五步研创流水线总控 MCP 服务 (study-harness-pipeline) 测试通过")

    def test_05_mcp_server_registration(self):
        """测试 5: mcp_server.py 工具注册完整性"""
        self.assertTrue(hasattr(mcp_server, "verify_fact_or_code"))
        self.assertTrue(hasattr(mcp_server, "inspect_study_pipeline"))
        print("  [✓] MCP Server 第 10 讲工具挂载完整性测试通过")

if __name__ == "__main__":
    unittest.main()
