#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chapter_09.py: 专栏第 09 讲配套 SKILL 与 MCP 自动化集成测试套件
验证:
1. 实验策划技能 (SKILL experiment-planner) 规范与执行
2. 青霉素反常机遇洞察服务 (MCP 工具 detect_serendipity)
3. 张伯伦多假说打擂服务 (MCP 工具 chamberlin_hypotheses)
4. 达尔文打脸笔记技能 (SKILL darwin-critic-observer) 规范与执行
5. MCP Server (mcp_server.py) 第 09 讲工具挂载完整性
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

class TestChapter09Suite(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        api_key = get_api_key()
        if not api_key:
            raise unittest.SkipTest("未配置有效的 DEEPSEEK_API_KEY，跳过在线大模型测试。")
        print(f"\n[+] 正在启动第 09 讲集成测试，API Key: {api_key[:6]}...")

    def test_01_experiment_planner_skill(self):
        """测试 1: 实验策划技能 (SKILL experiment-planner) 规范与执行"""
        skill_file = PROJECT_ROOT / "system" / "skills" / "experiment-planner" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "experiment-planner SKILL.md 不存在")
        self.assertIn("name: experiment-planner", skill_file.read_text(encoding="utf-8"))

        script_path = PROJECT_ROOT / "system" / "skills" / "experiment-planner" / "scripts" / "planner.py"
        spec = importlib.util.spec_from_file_location("planner", script_path)
        planner_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(planner_mod)

        test_out = PROJECT_ROOT / "tests" / "output_test_planner.md"
        query = "假说：在多智能体协同编写代码时，引入冷面法官裁判角色可使长程死锁率降低 80%。"
        res = planner_mod.plan_experiment(query, topic_name="多智能体代码评审对照实验", output_path=str(test_out))

        self.assertIn("渐进式实验策划与对照设计方案", res["report"])
        self.assertIn("Pilot", res["report"])
        self.assertIn("对照", res["report"])
        self.assertTrue(test_out.exists(), "未能生成预期的实验策划书")
        test_out.unlink()
        print("  [✓] 实验策划技能 (SKILL experiment-planner) 测试通过")

    def test_02_detect_serendipity_mcp(self):
        """测试 2: 青霉素反常机遇洞察 MCP 服务 (detect_serendipity)"""
        anomaly = "原本设定的高并发性能压测脚本发生网络丢包，但异常捕获模块的内存占用不升反降 70%，且吞吐量出现离群毛刺峰值。"
        context = "压测 Rust 异步 Actor 消息中间件，预期丢包时应该堆积重试导致内存暴涨。"
        test_out = PROJECT_ROOT / "tests" / "output_test_serendipity.md"
        res_text = mcp_server.detect_serendipity(anomaly, context=context, output_file=str(test_out))

        self.assertIn("青霉素反常机遇洞察专报", res_text)
        self.assertIn("颠覆性假说", res_text)
        self.assertTrue(test_out.exists(), "未能生成预期的机遇洞察专报")
        test_out.unlink()
        print("  [✓] 青霉素反常机遇洞察 MCP 服务 (serendipity-radar) 测试通过")

    def test_03_chamberlin_hypotheses_mcp(self):
        """测试 3: 张伯伦多假说打擂 MCP 服务 (chamberlin_hypotheses)"""
        problem = "复杂多模态模型在处理专业医学影像时，轻度模糊图像的诊断准确率反常地高于 4K 超清图像。"
        test_out = PROJECT_ROOT / "tests" / "output_test_chamberlin.md"
        res_text = mcp_server.chamberlin_hypotheses(problem, hypothesis_count=3, output_file=str(test_out))

        self.assertIn("张伯伦多重工作假说打擂专报", res_text)
        self.assertIn("假说", res_text)
        self.assertIn("判决实验", res_text)
        self.assertTrue(test_out.exists(), "未能生成预期的多假说打擂专报")
        test_out.unlink()
        print("  [✓] 张伯伦多假说打擂 MCP 服务 (chamberlin-hypotheses) 测试通过")

    def test_04_darwin_critic_observer_skill(self):
        """测试 4: 达尔文打脸笔记技能 (SKILL darwin-critic-observer) 规范与执行"""
        skill_file = PROJECT_ROOT / "system" / "skills" / "darwin-critic-observer" / "SKILL.md"
        self.assertTrue(skill_file.exists(), "darwin-critic-observer SKILL.md 不存在")
        self.assertIn("name: darwin-critic-observer", skill_file.read_text(encoding="utf-8"))

        script_path = PROJECT_ROOT / "system" / "skills" / "darwin-critic-observer" / "scripts" / "darwin.py"
        spec = importlib.util.spec_from_file_location("darwin", script_path)
        darwin_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(darwin_mod)

        test_out = PROJECT_ROOT / "tests" / "output_test_darwin.md"
        obs = "线上 A/B 测试发现：新上线的大模型检索增强架构在北美节点转化率提升 15%，但在日韩节点转化率直接下跌 28%，用户停留时长腰斩。"
        hypo = "我们团队坚信新的语义向量嵌入检索方案在所有语种和场景下均大幅优于传统 BM25 检索。"
        res = darwin_mod.record_darwin_critique(obs, hypothesis_text=hypo, output_path=str(test_out))

        self.assertIn("达尔文打脸笔记与批判性观察专报", res["report"])
        self.assertIn("纯物理表象", res["report"])
        self.assertTrue(test_out.exists(), "未能生成预期的达尔文打脸笔记")
        test_out.unlink()
        print("  [✓] 达尔文打脸笔记技能 (SKILL darwin-critic-observer) 测试通过")

    def test_05_mcp_server_registration(self):
        """测试 5: mcp_server.py 工具注册完整性"""
        self.assertTrue(hasattr(mcp_server, "detect_serendipity"))
        self.assertTrue(hasattr(mcp_server, "chamberlin_hypotheses"))
        print("  [✓] MCP Server 工具挂载完整性测试通过")

if __name__ == "__main__":
    unittest.main()
