# -*- coding: utf-8 -*-
"""
Integration test with live DeepSeek API.
Verifies real API call and full tool loop.
"""

import os
import pytest
from study_harness.client import get_deepseek_client
from study_harness.engine import HarnessEngine

@pytest.mark.skipif(not os.environ.get("DEEPSEEK_API_KEY"), reason="需要配置 DEEPSEEK_API_KEY")
def test_live_deepseek_single_call():
    client = get_deepseek_client()
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": "请只回复两个字：收到"}]
    )
    content = resp.choices[0].message.content.strip()
    assert "收到" in content

@pytest.mark.skipif(not os.environ.get("DEEPSEEK_API_KEY"), reason="需要配置 DEEPSEEK_API_KEY")
def test_live_deepseek_engine_loop(tmp_path):
    test_file = tmp_path / "live_test.txt"
    test_file.write_text("Study-Harness 真实在线联调测试", encoding="utf-8")

    engine = HarnessEngine(model="deepseek-chat", temperature=0.0)
    task = f"请读取文件 '{test_file}'，如果包含'联调'二字，请向我回复'测试通过'。"

    result = engine.run(user_task=task, max_turns=4, verbose=False)
    assert result["completed"] is True
    assert any(a["tool"] == "read_file" for a in result["actions"])
    assert "测试通过" in result["final_answer"]
