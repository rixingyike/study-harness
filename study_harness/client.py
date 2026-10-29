# -*- coding: utf-8 -*-
"""
DeepSeek Client Factory.
Initializes OpenAI SDK client targeting DeepSeek API.
"""

import os
from pathlib import Path
from openai import OpenAI

def load_env_file():
    """Load environment variables from .env if present."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and v:
                        os.environ[k] = v

def get_deepseek_client(api_key: str = None, base_url: str = None) -> OpenAI:
    """
    Returns an OpenAI client configured for DeepSeek.
    """
    load_env_file()
    
    resolved_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
    resolved_base = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    if not resolved_key:
        raise ValueError("未找到 DEEPSEEK_API_KEY，请在 .env 文件或环境变量中配置。")

    return OpenAI(
        api_key=resolved_key,
        base_url=resolved_base
    )
