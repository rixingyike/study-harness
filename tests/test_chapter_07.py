#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chapter_07.py: 专栏第 07 讲配套 SKILL 与 MCP 自动化集成测试套件
验证:
1. DeepSeek 统一底层通信连通性
2. 科学家性格画像与潜能诊断技能 (SKILL scientist-profiler)
3. 异构双智能体协同推演器服务 (MCP 工具 collaborate_duo)
4. 课题战略审查与四维打分服务 (MCP 工具 evaluate_topic)
5. MCP Server (mcp_server.py) 工具挂载完整性
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

from deepseek_client import get_api_key, call_deepseek
import mcp_server

class TestChapter07Suite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        api_key = get_api_key()
        if not api_key:
            raise unittest.SkipTest("未配置有效的 DEEPSEEK_API_KEY，跳过在线大模型测试。")
        print(f"\n[+] 正在启动第 07 讲集成测试，API Key: {api_key[:6]}...")

    def test_01_deepseek_connectivity(self):
        """测试 1: 底层通信接口健康探测"""
        reply = call_deepseek([{"role": "user", "content": "请回复四个字：通信正常"}], max_tokens=20)
        self.assertIn("通信正常", reply)
        print("  [✓] DeepSeek 通信正常")

    def test_02_scientist_profiler_skill(self):
        """测试 2: 科学家潜能诊断技能 (SKILL scientist-profiler) 功能验证"""
        # 1. 验证 SKILL 规范文件存在且合规
        skill_file = PROJECT_ROOT / "system" / "skills" / "scientist-profiler" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "scientist-profiler SKILL.md 不存在")
        skill_text = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: scientist-profiler", skill_text)
        
        # 2. 动态加载并执行该 Skill 的底层执行模块
        script_path = PROJECT_ROOT / "system" / "skills" / "scientist-profiler" / "scripts" / "profiler.py"
        spec = importlib.util.spec_from_file_location("profiler", script_path)
        profiler_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(profiler_mod)

        sample_bio = (
            "我大学时数学很好，但总是被教授批评‘不务正业’，因为我喜欢琢磨生物进化论。"
            "工作后我受不了领导每天查进度，我常常在夜里散步时突然想到新方案。"
            "但我最大的弱点是容易开好几个课题却很少能全部收尾。"
        )
        test_out = PROJECT_ROOT / "tests" / "output_test_profile.md"
        res = profiler_mod.profile_scientist(sample_bio, scholar_name="测试研究员", output_path=str(test_out))
        report_str = res["report"]
        
        self.assertIn("学者性格画像与潜能诊断报告", report_str)
        self.assertIn("反应型", report_str)
        self.assertTrue("内在驱动" in report_str or "爱因斯坦" in report_str)
        self.assertTrue("推测型" in report_str or "浪漫派" in report_str)
        self.assertTrue(test_out.exists(), "未能生成预期的诊断输出文件")
        test_out.unlink()  # 清理临时文件
        print("  [✓] 科学家潜能诊断技能 (SKILL scientist-profiler) 测试通过")

    def test_03_speculative_systematic_duo_mcp(self):
        """测试 3: 异构双智能体协同推演 MCP 服务 (collaborate_duo) 流程测试"""
        sample_topic = "能否利用纳米磁性颗粒自动清除血管中的早期斑块？"
        test_out = PROJECT_ROOT / "tests" / "output_test_duo.md"
        report_str = mcp_server.collaborate_duo(sample_topic, output_file=str(test_out))
        
        self.assertIn("推测先锋", report_str)
        self.assertIn("条理法官", report_str)
        self.assertTrue(test_out.exists(), "未能生成预期的双智能体报告文件")
        test_out.unlink()  # 清理临时文件
        print("  [✓] 异构双智能体协同推演 MCP 服务 (collaborate_duo) 测试通过")

    def test_04_topic_evaluator_mcp(self):
        """测试 4: 课题打分 MCP 服务 (evaluate_topic) 测试"""
        sample_plan = (
            "课题：研发超导量子芯片常温探针。\n"
            "计划：团队由三名博士组成，自主安排实验细节，但必须接受每周一次的里程碑进度评审。\n"
            "如果连续三个月无法观测到信号，课题自动终止并转向备用方案。"
        )
        test_out = PROJECT_ROOT / "tests" / "output_test_topic.md"
        report_str = mcp_server.evaluate_topic(sample_plan, topic_title="量子芯片探针", output_file=str(test_out))
        
        self.assertIn("课题战略审查与综合评估报告", report_str)
        self.assertIn("四维量化评分明细表", report_str)
        self.assertTrue(test_out.exists(), "未能生成预期的课题审查文件")
        test_out.unlink()  # 清理临时文件
        print("  [✓] 课题打分 MCP 服务 (evaluate_topic) 测试通过")

    def test_05_mcp_server_tools_registered(self):
        """测试 5: 验证 mcp_server.py 中挂载的 MCP 服务工具完整性"""
        registered_funcs = ["collaborate_duo", "evaluate_topic", "get_study_harness_summary", "calculate_token_cost"]
        for fn in registered_funcs:
            self.assertTrue(hasattr(mcp_server, fn), f"mcp_server 缺失预期工具函数: {fn}")
        self.assertFalse(hasattr(mcp_server, "profile_scientist"), "profile_scientist 是独立技能，不应挂在 mcp_server")
        print("  [✓] MCP Server 工具挂载完整性测试通过")

if __name__ == "__main__":
    unittest.main()
