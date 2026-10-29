#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_think_act_observe_loop.py: Think-Act-Observe 三级循环与工具调用完整演示
对应专栏第 02 篇第三节：单文件手搓状态机闭环引擎。

【生成核心循环代码的提示词】：
在 study-harness 项目根目录下，直接编写并写入 02_think_act_observe_loop.py 文件：
1. 使用 openai 库连接 DeepSeek（deepseek-chat，base_url="https://api.deepseek.com"）；
2. 实现两个本地文件工具 read_file 与 write_file，并定义标准 Tools Schema；
3. 编写 run_harness_loop(user_task, max_turns=5)，用 while 循环实现 Think、Act、Observe 三级状态流转：
   - Think：向模型发送上下文。若无 tool_calls，打印结论并退出；
   - Act：解析 tool_calls 并执行本地工具；
   - Observe：将执行结果以 role: "tool" 塞回上下文，触发下一轮思考；
4. max_turns 步数超限强制刹车；
5. 在 __main__ 写入测试：读取“原始笔记.txt”，提炼核心方法论并写入“提炼报告.txt”。
"""

import os
import json
from pathlib import Path
from openai import OpenAI

def load_env():
    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("DEEPSEEK_API_KEY="):
                    os.environ["DEEPSEEK_API_KEY"] = line.split("=", 1)[1].strip().strip("'\"")

load_env()

# 1. 准备连接 DeepSeek 的客户端
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", "你的_DeepSeek_API_Key"),
    base_url="https://api.deepseek.com"
)

# ----------------------------------------------------
# 2. 本地真实工具函数（这是智能体能触碰物理世界的“双手”）
# ----------------------------------------------------
def read_file(file_path: str) -> str:
    """读取指定路径的本地文本文件"""
    print(f"  [物理操作 Act] 正在打开并读取本地文件：{file_path}")
    try:
        if not os.path.exists(file_path):
            return f"错误：文件 {file_path} 根本不存在，请核对路径。"
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"读取文件时发生异常：{str(e)}"

def write_file(file_path: str, content: str) -> str:
    """向指定路径写入文本文件"""
    print(f"  [物理操作 Act] 正在向本地文件写入内容：{file_path}")
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"成功：已成功向 {file_path} 写入 {len(content)} 个字符。"
    except Exception as e:
        return f"写入文件时发生异常：{str(e)}"

# 工具映射表：方便根据模型吐出来的名字找到真实函数
TOOL_MAP = {
    "read_file": read_file,
    "write_file": write_file
}

# ----------------------------------------------------
# 3. 把工具规矩打包成 OpenAI 标准的描述表（Tools Schema）
# ----------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容的工具",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "要读取的文件绝对路径或相对路径"}
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
                    "file_path": {"type": "string", "description": "要写入的文件路径"},
                    "content": {"type": "string", "description": "要写入的纯文本内容"}
                },
                "required": ["file_path", "content"]
            }
        }
    }
]

# ----------------------------------------------------
# 4. Harness 核心引擎：Think -> Act -> Observe 状态机循环
# ----------------------------------------------------
def run_harness_loop(user_task: str, max_turns: int = 5):
    """
    驱动大模型在思考、行动与观察之间循环流转，直至任务完成
    """
    print(f"\n================ 开始执行任务 ================")
    print(f"目标：{user_task}\n")
    
    # 初始化上下文记忆
    messages = [
        {
            "role": "system",
            "content": "你是一位脚踏实地的学术研创助手。请善用本地工具查看资料、解决问题。干完活请向用户简明汇报。"
        },
        {
            "role": "user",
            "content": user_task
        }
    ]

    turn = 0
    while turn < max_turns:
        turn += 1
        print(f"\n--- 【第 {turn} 轮循环循环跳动】 ---")
        
        # 步骤一：【Think 思考】
        # 把全部上下文喂给大模型，让它结合当前进展决定下一步
        print(f"  [思考中 Think] 大模型正在审视历史并盘算策略...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            temperature=0.2  # 调低随机度，让做事更加扎实严谨
        )
        
        msg = response.choices[0].message
        messages.append(msg) # 将大模型的思考或发出的指令记入上下文

        # 分支判断：如果大模型觉得不需要动用工具，说明任务已完成或已经可以直接回复
        if not msg.tool_calls:
            print(f"\n[任务收尾 Finish] 大模型认为任务已达成，最终交付结果：")
            print(msg.content)
            break

        # 步骤二与三：【Act 行动】与【Observe 观察】
        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            print(f"  [意图确认] 大模型决定动用工具：{tool_name}，参数：{tool_args}")
            
            # 【Act 真实行动】
            func = TOOL_MAP.get(tool_name)
            if func:
                observation = func(**tool_args)
            else:
                observation = f"错误：未注册的工具名称 {tool_name}"
            
            # 【Observe 真实观察】
            print(f"  [环境反馈 Observe] 物理世界返回客观事实：{observation}")
            
            # 将工具产出的真实观察事实，打包成 role: 'tool' 的消息塞回记忆
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(observation)
            })

    if turn >= max_turns:
        print(f"\n[安全触发 Stop] 达到最大步数限制（{max_turns}步），强行刹车，防止死循环。")

# ----------------------------------------------------
# 5. 实战检验：让我们给它派发一个真实的研创整理任务
# ----------------------------------------------------
if __name__ == "__main__":
    # 先在本地随手造一个测试素材文件
    test_note = "贝弗里奇在《科学研究的艺术》中指出：批判性阅读是发现科学假说矛盾的最快途径。"
    with open("原始笔记.txt", "w", encoding="utf-8") as f:
        f.write(test_note)
        
    # 给 Harness 下达一个跨越读写的综合任务
    user_prompt = "请读取本地的'原始笔记.txt'，提炼出它的核心方法论，并把提炼结果写进一个新的'提炼报告.txt'文件中。"
    
    run_harness_loop(user_prompt)
