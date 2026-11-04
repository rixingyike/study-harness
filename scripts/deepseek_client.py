#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deepseek_client.py: Study-Harness 统一的大模型客户端与通信基础组件
支持从环境变量与本地 .env 文件中自动解析 DEEPSEEK_API_KEY 与 DEEPSEEK_BASE_URL。
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_api_key() -> str:
    """获取有效的 DeepSeek API Key"""
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key and not key.endswith("34e3"):  # 避免过期的失效测试 Key
        return key
    
    candidates = [
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / "chat_web" / "backend" / ".env",
        Path("/Users/jsmn/workspace/cloud-editor/.env"),
        Path.home() / ".env"
    ]
    for p in candidates:
        if p.exists():
            try:
                for line in p.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line.startswith("DEEPSEEK_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val and not val.endswith("34e3"):
                            return val
            except Exception:
                continue
    return key

def get_base_url() -> str:
    """获取 DeepSeek Base URL"""
    return os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")

def call_deepseek(
    messages: List[Dict[str, str]],
    model: str = "deepseek-chat",
    temperature: float = 0.2,
    max_tokens: int = 3500,
    timeout: int = 120
) -> str:
    """
    通用 DeepSeek 文本生成接口
    
    参数:
        messages: 对话消息列表 [{"role": "system"/"user"/"assistant", "content": "..."}]
        model: 模型标识，默认 "deepseek-chat" (DeepSeek-V3)
        temperature: 执行温度，严格分析建议 0.2，发散想象建议 0.8
        max_tokens: 最大生成 Token 数
        timeout: 请求超时秒数
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("未检测到有效的 DEEPSEEK_API_KEY，请检查 .env 文件或环境变量。")
    
    base_url = get_base_url()
    url = f"{base_url}/chat/completions"
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            return resp_data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"DeepSeek API 请求失败 (HTTP {e.code}): {err_body}")
    except Exception as e:
        raise RuntimeError(f"调用 DeepSeek 异常: {str(e)}")

if __name__ == "__main__":
    print(f"[*] API Key 检测: {'已配置 (' + get_api_key()[:6] + '...)' if get_api_key() else '未配置'}")
    print(f"[*] Base URL: {get_base_url()}")
