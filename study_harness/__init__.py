"""
Study-Harness: AI Scholar Research & Creation Engine.
Core Think-Act-Observe Loop Implementation.
"""

from .client import get_deepseek_client
from .tools import read_file, write_file, TOOLS_SCHEMA, TOOL_MAP
from .engine import HarnessEngine, run_harness_loop

__all__ = [
    "get_deepseek_client",
    "read_file",
    "write_file",
    "TOOLS_SCHEMA",
    "TOOL_MAP",
    "HarnessEngine",
    "run_harness_loop",
]
