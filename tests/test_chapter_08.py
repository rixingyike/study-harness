#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chapter_08.py: 专栏第 08 讲配套 SKILL 与 MCP 自动化集成测试套件
验证:
1. 想象力激发技能 (SKILL imagination-spark)
2. 反刍随身记与闪念捕获服务 (MCP 工具 ruminate_spark / get_daily_rumination)
3. 侦探与法官双智能体推演服务 (MCP 工具 dual_agent_reason)
4. 死锁破局急救技能 (SKILL deadlock-breaker)
5. MCP Server (mcp_server.py) 第 08 讲工具挂载完整性
"""

import os
import sys
import unittest
import importlib.util
import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "system" / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "system" / "scripts"))

from deepseek_client import get_api_key
import mcp_server

class TestChapter08Suite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        api_key = get_api_key()
        if not api_key:
            raise unittest.SkipTest("未配置有效的 DEEPSEEK_API_KEY，跳过在线大模型测试。")
        print(f"\n[+] 正在启动第 08 讲集成测试，API Key: {api_key[:6]}...")

    def test_01_imagination_spark_skill(self):
        """测试 1: 想象力激发技能 (SKILL imagination-spark) 规范与执行"""
        skill_file = PROJECT_ROOT / "system" / "skills" / "imagination-spark" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "imagination-spark SKILL.md 不存在")
        self.assertIn("name: imagination-spark", skill_file.read_text(encoding="utf-8"))

        script_path = PROJECT_ROOT / "system" / "skills" / "imagination-spark" / "scripts" / "spark.py"
        spec = importlib.util.spec_from_file_location("spark", script_path)
        spark_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(spark_mod)

        test_out = PROJECT_ROOT / "tests" / "output_test_spark.md"
        query = "大模型在长上下文跨文件修改时频繁出现幻觉和接口错位。"
        res = spark_mod.spark_imagination(query, topic_name="长上下文接口对齐", output_path=str(test_out))

        self.assertIn("想象力激发与 Why & How", res["report"])
        self.assertIn("Why", res["report"])
        self.assertIn("How", res["report"])
        self.assertTrue(test_out.exists(), "未能生成预期的想象力激发分析文件")
        test_out.unlink()
        print("  [✓] 想象力激发技能 (SKILL imagination-spark) 测试通过")

    def test_02_intuition_ruminator_mcp(self):
        """测试 2: 反刍随身记与闪念捕获 MCP 服务 (ruminate_spark / get_daily_rumination)"""
        spark_content = "测试闪念：大模型多轮压缩机制与潜意识遗忘机制高度同构。"
        res = mcp_server.ruminate_spark(spark_content, category="直觉灵感", tags="大模型, 潜意识")
        self.assertIn("闪念已成功归档并从工作记忆中卸载", res)

        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        daily_log = mcp_server.get_daily_rumination(today_str)
        self.assertIn("研创反刍与闪念捕获日志", daily_log)
        self.assertIn("测试闪念", daily_log)
        print("  [✓] 反刍随身记与闪念捕获 MCP 服务 (intuition-ruminator) 测试通过")

    def test_03_dual_agent_reason_mcp(self):
        """测试 3: 侦探与法官双智能体推演 MCP 服务 (dual_agent_reason)"""
        sample_clue = "线上分布式系统每到周一凌晨两点偶发死锁，但系统日志里没有任何慢查询记录。"
        test_out = PROJECT_ROOT / "tests" / "output_test_dual_reason.md"
        res_text = mcp_server.dual_agent_reason(sample_clue, output_file=str(test_out))

        self.assertIn("阶段一：【敏锐侦探】", res_text)
        self.assertIn("阶段二：【冷面法官】", res_text)
        self.assertTrue(test_out.exists(), "未能生成预期的双智能体推演专报")
        test_out.unlink()
        print("  [✓] 侦探与法官双智能体推演 MCP 服务 (dual-agent-reasoning) 测试通过")

    def test_04_deadlock_breaker_skill(self):
        """测试 4: 死锁破局急救技能 (SKILL deadlock-breaker) 规范与执行"""
        skill_file = PROJECT_ROOT / "system" / "skills" / "deadlock-breaker" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "deadlock-breaker SKILL.md 不存在")
        self.assertIn("name: deadlock-breaker", skill_file.read_text(encoding="utf-8"))

        script_path = PROJECT_ROOT / "system" / "skills" / "deadlock-breaker" / "scripts" / "breaker.py"
        spec = importlib.util.spec_from_file_location("breaker", script_path)
        breaker_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(breaker_mod)

        test_out = PROJECT_ROOT / "tests" / "output_test_breaker.md"
        problem = "智能体长程规划在第十步发生状态爆炸，算力崩盘，死磕三天毫无头绪。"
        res = breaker_mod.break_deadlock(problem, problem_name="长程规划状态爆炸", output_path=str(test_out))

        self.assertIn("难题死锁破局急救处方", res["prescription"])
        self.assertIn("第一味药", res["prescription"])
        self.assertIn("第二味药", res["prescription"])
        self.assertIn("第三味药", res["prescription"])
        self.assertTrue(test_out.exists(), "未能生成预期的破局急救处方文件")
        test_out.unlink()
        print("  [✓] 死锁破局急救技能 (SKILL deadlock-breaker) 测试通过")

    def test_05_mcp_server_tools_registered(self):
        """测试 5: 验证 mcp_server.py 中挂载的第 08 讲工具完整性"""
        expected_tools = ["ruminate_spark", "get_daily_rumination", "dual_agent_reason"]
        for tool_name in expected_tools:
            self.assertTrue(hasattr(mcp_server, tool_name), f"mcp_server 缺失预期工具: {tool_name}")
        print("  [✓] MCP Server 第 08 讲工具挂载完整性测试通过")

if __name__ == "__main__":
    unittest.main()
