#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example 01: 基础调用演示 (OpenAI SDK + DeepSeek API)
对应专栏第 02 篇第一节：传统的“无状态、单次问答”裸奔调用方式。

【生成该代码的 AI 提示词】：
请使用 Python 3 和官方 openai 库（连接 DeepSeek API，base_url="https://api.deepseek.com"，模型 deepseek-chat），编写一段最简的单次问答调用代码：
1. 从环境变量 DEEPSEEK_API_KEY 中读取密钥并初始化 OpenAI 客户端；
2. 向模型发送一条简单的测试问答（如“你好！请问你能帮我干活吗？”）；
3. 打印出大模型的回复内容。
"""

import os
from openai import OpenAI

def main():
    # 1. 准备好客户端，优先从 .env 读取
    from pathlib import Path
    api_key = None
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("DEEPSEEK_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip("'\"")
    if not api_key:
        api_key = os.environ.get("DEEPSEEK_API_KEY")

    client = OpenAI(
        api_key=api_key or "你的_DeepSeek_API_Key",
        base_url="https://api.deepseek.com"
    )

    print(">>> 正在向 DeepSeek 发送单次问答请求...")
    # 2. 发送一句最普通的问答请求
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": "你好！请问你能帮我干活吗？"}
        ]
    )

    # 3. 打印出大模型吐出来的回复
    print("\n大模型回答：\n", response.choices[0].message.content)
    print("\n[分析]：请求完成，连接立即断开，模型无法接触本地文件与环境。")

if __name__ == "__main__":
    main()
