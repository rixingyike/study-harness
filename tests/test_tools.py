# -*- coding: utf-8 -*-
"""
Unit tests for study_harness.tools:
Validates read_file and write_file deterministic behavior.
"""

import os
import tempfile
import pytest
from study_harness.tools import read_file, write_file, TOOL_MAP, TOOLS_SCHEMA

def test_read_file_existing():
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as f:
        f.write("hello study harness")
        temp_path = f.name

    try:
        content = read_file(temp_path)
        assert content == "hello study harness"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def test_read_file_not_found():
    result = read_file("/tmp/this_file_does_not_exist_12345.txt")
    assert "错误：文件" in result
    assert "根本不存在" in result

def test_write_file_new():
    temp_dir = tempfile.mkdtemp()
    target_file = os.path.join(temp_dir, "test_write.txt")

    try:
        res = write_file(target_file, "测试写入内容")
        assert "成功：已成功向" in res
        assert os.path.exists(target_file)
        with open(target_file, "r", encoding="utf-8") as f:
            assert f.read() == "测试写入内容"
    finally:
        if os.path.exists(target_file):
            os.remove(target_file)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

def test_tools_schema_definition():
    assert len(TOOLS_SCHEMA) == 2
    tool_names = [t["function"]["name"] for t in TOOLS_SCHEMA]
    assert "read_file" in tool_names
    assert "write_file" in tool_names
    assert "read_file" in TOOL_MAP
    assert "write_file" in TOOL_MAP
