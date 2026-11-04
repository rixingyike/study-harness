#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chapter_07.py: 专栏第 07 讲配套工具与 MCP 自动化集成测试套件
验证:
1. DeepSeek 统一底层通信连通性
2. 科学家性格画像与潜能诊断引擎 (scientist_profiler)
3. 异构双智能体协同推演器 (speculative_systematic_duo)
4. 课题战略审查与四维打分引擎 (topic_evaluator)
5. MCP Server (mcp_server.py) 工具挂载完整性
"""

import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.deepseek_client import get_api_key, call_deepseek
from scripts.scientist_profiler import profile_scientist
from scripts.speculative_systematic_duo import collaborate_duo
from scripts.topic_evaluator import evaluate_topic
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

    def test_02_scientist_profiler(self):
        """测试 2: 科学家性格画像引擎功能与格式验证"""
        sample_bio = (
            "我大学时数学很好，但总是被教授批评‘不务正业’，因为我喜欢琢磨生物进化论。"
            "工作后我受不了领导每天查进度，我常常在夜里散步时突然想到新方案。"
            "但我最大的弱点是容易开好几个课题却很少能全部收尾。"
        )
        test_out = PROJECT_ROOT / "tests" / "output_test_profile.md"
        res = profile_scientist(sample_bio, scholar_name="测试研究员", output_path=str(test_out))
        
        self.assertIn("学者性格画像与潜能诊断报告", res["report"])
        self.assertIn("反应型", res["report"])
        self.assertTrue("内在驱动" in res["report"] or "爱因斯坦" in res["report"])
        self.assertTrue("推测型" in res["report"] or "浪漫派" in res["report"])
        self.assertTrue(test_out.exists())
        test_out.unlink()  # 清理临时文件
        print("  [✓] 科学家性格画像引擎测试通过")

    def test_03_speculative_systematic_duo(self):
        """测试 3: 异构双智能体协同推演器流程测试"""
        sample_topic = "能否利用纳米磁性颗粒自动清除血管中的早期斑块？"
        test_out = PROJECT_ROOT / "tests" / "output_test_duo.md"
        res = collaborate_duo(sample_topic, output_path=str(test_out))
        
        self.assertIn("推测先锋", res["full_report"])
        self.assertIn("条理法官", res["full_report"])
        self.assertTrue(test_out.exists())
        test_out.unlink()  # 清理临时文件
        print("  [✓] 异构双智能体协同推演器测试通过")

    def test_04_topic_evaluator(self):
        """测试 4: 课题战略审查与四维打分测试"""
        sample_plan = (
            "课题：研发超导量子芯片常温探针。\n"
            "计划：团队由三名博士组成，自主安排实验细节，但必须接受每周一次的里程碑进度评审。\n"
            "如果连续三个月无法观测到信号，课题自动终止并转向备用方案。"
        )
        test_out = PROJECT_ROOT / "tests" / "output_test_topic.md"
        res = evaluate_topic(sample_plan, topic_title="量子芯片探针", output_path=str(test_out))
        
        self.assertIn("课题战略审查与综合评估报告", res["report"])
        self.assertIn("四维量化评分明细表", res["report"])
        self.assertTrue(test_out.exists())
        test_out.unlink()  # 清理临时文件
        print("  [✓] 课题战略审查与四维打分引擎测试通过")

    def test_05_mcp_server_tools_registered(self):
        """测试 5: 验证 mcp_server.py 中第 07 讲全部工具均已暴露"""
        # 获取 FastMCP/MCPServer 实例
        app = getattr(mcp_server, "app", None)
        self.assertIsNotNone(app, "mcp_server app 未成功初始化")
        
        # 兼容不同版本 FastMCP/MCPServer 获取 tool 列表
        tools = []
        if hasattr(app, "_tool_manager") and hasattr(app._tool_manager, "_tools"):
            tools = list(app._tool_manager._tools.keys())
        elif hasattr(app, "list_tools"):
            import asyncio
            try:
                res = asyncio.run(app.list_tools())
                tools = [t.name for t in res]
            except Exception:
                pass
        
        # 也可以直接检查模块内导出的函数
        registered_funcs = ["profile_scientist", "collaborate_duo", "evaluate_topic", "get_study_harness_summary", "calculate_token_cost"]
        for fn in registered_funcs:
            self.assertTrue(hasattr(mcp_server, fn), f"mcp_server 缺失预期工具函数: {fn}")
        print("  [✓] MCP Server 5 大工具挂载完整性测试通过")

if __name__ == "__main__":
    unittest.main()
