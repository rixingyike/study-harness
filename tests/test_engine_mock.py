# -*- coding: utf-8 -*-
"""
Unit tests for HarnessEngine state machine using Mocks.
Validates Think -> Act -> Observe transitions and safety braking.
"""

import json
from unittest.mock import MagicMock
from study_harness.engine import HarnessEngine

def create_mock_tool_call(call_id: str, func_name: str, arguments: dict):
    call = MagicMock()
    call.id = call_id
    call.function.name = func_name
    call.function.arguments = json.dumps(arguments, ensure_ascii=False)
    return call

def test_engine_think_act_observe_convergence(tmp_path):
    # Setup test files
    input_file = tmp_path / "note.txt"
    output_file = tmp_path / "summary.txt"
    input_file.write_text("贝弗里奇的科研艺术", encoding="utf-8")

    # Mock responses for 3 turns:
    # Turn 1: Model requests read_file
    resp_turn1 = MagicMock()
    msg_1 = MagicMock()
    msg_1.content = "我需要先读取笔记内容"
    msg_1.tool_calls = [
        create_mock_tool_call("call_01", "read_file", {"file_path": str(input_file)})
    ]
    resp_turn1.choices = [MagicMock(message=msg_1)]

    # Turn 2: Model requests write_file with summary
    resp_turn2 = MagicMock()
    msg_2 = MagicMock()
    msg_2.content = "我已经提取出核心观点，现在写入摘要"
    msg_2.tool_calls = [
        create_mock_tool_call("call_02", "write_file", {
            "file_path": str(output_file),
            "content": "提炼核心：科研是一门实践艺术。"
        })
    ]
    resp_turn2.choices = [MagicMock(message=msg_2)]

    # Turn 3: Model finishes task
    resp_turn3 = MagicMock()
    msg_3 = MagicMock()
    msg_3.content = "任务已圆满完成！报告已保存至 summary.txt。"
    msg_3.tool_calls = None
    resp_turn3.choices = [MagicMock(message=msg_3)]

    # Setup mock client
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = [resp_turn1, resp_turn2, resp_turn3]

    engine = HarnessEngine(client=mock_client)
    result = engine.run(user_task="请整理 note.txt 并输出 summary.txt", max_turns=5, verbose=False)

    assert result["completed"] is True
    assert result["turns"] == 3
    assert "任务已圆满完成" in result["final_answer"]
    assert len(result["actions"]) == 2

    # Check action 1
    assert result["actions"][0]["tool"] == "read_file"
    assert result["actions"][0]["observation"] == "贝弗里奇的科研艺术"

    # Check action 2
    assert result["actions"][1]["tool"] == "write_file"
    assert "成功：已成功向" in result["actions"][1]["observation"]
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "提炼核心：科研是一门实践艺术。"

def test_engine_safety_brake_max_turns():
    # Model that continuously requests a tool call and never stops
    resp_loop = MagicMock()
    msg_loop = MagicMock()
    msg_loop.content = "继续尝试..."
    msg_loop.tool_calls = [
        create_mock_tool_call("call_loop", "read_file", {"file_path": "/tmp/dummy.txt"})
    ]
    resp_loop.choices = [MagicMock(message=msg_loop)]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = resp_loop

    engine = HarnessEngine(client=mock_client)
    result = engine.run(user_task="无限循环死锁测试", max_turns=3, verbose=False)

    assert result["completed"] is False
    assert result["turns"] == 3
    assert result["final_answer"] is None
    assert len(result["actions"]) == 3
