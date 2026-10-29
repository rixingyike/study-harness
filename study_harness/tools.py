# -*- coding: utf-8 -*-
"""
Local Tool Functions and Schema Definitions.
Implements deterministic, sandboxed local file operations.
"""

import os
from typing import Dict, Any, Callable

def read_file(file_path: str) -> str:
    """读取指定路径的本地文本文件"""
    try:
        resolved_path = os.path.abspath(file_path)
        if not os.path.exists(resolved_path):
            return f"错误：文件 {file_path} 根本不存在，请核对路径。"
        with open(resolved_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取文件时发生异常：{str(e)}"

def write_file(file_path: str, content: str) -> str:
    """向指定路径写入文本文件"""
    try:
        resolved_path = os.path.abspath(file_path)
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True) if os.path.dirname(resolved_path) else None
        with open(resolved_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功：已成功向 {file_path} 写入 {len(content)} 个字符。"
    except Exception as e:
        return f"写入文件时发生异常：{str(e)}"

# 工具映射表：方便根据模型返回的工具名称执行对应的真实本地函数
TOOL_MAP: Dict[str, Callable[..., str]] = {
    "read_file": read_file,
    "write_file": write_file
}

# OpenAI 标准 Function Calling (Tools) 规范描述
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容的工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要读取的文件绝对路径或相对路径"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "向本地写入文本内容的工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "要写入的目标文件路径"
                    },
                    "content": {
                        "type": "string",
                        "description": "要写入的完整纯文本内容"
                    }
                },
                "required": ["file_path", "content"]
            }
        }
    }
]
