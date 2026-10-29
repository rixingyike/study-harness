# -*- coding: utf-8 -*-
"""
Harness Core Engine: Think-Act-Observe State Machine Loop.
Drives the language model to reason, act upon the local environment,
and observe empirical results in an iterative convergence loop.
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from .client import get_deepseek_client
from .tools import TOOLS_SCHEMA, TOOL_MAP

DEFAULT_SYSTEM_PROMPT = (
    "你是一位严谨求实的学术研创助手。请善用本地工具查看资料、验证数据并解决问题。"
    "每一步行动前先简要说明思考意图，干完活请向用户给出清晰的交付汇报。"
)

class HarnessEngine:
    def __init__(
        self,
        client: Optional[OpenAI] = None,
        model: str = "deepseek-chat",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        temperature: float = 0.2
    ):
        self.client = client or get_deepseek_client()
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.tools = TOOLS_SCHEMA
        self.tool_map = TOOL_MAP

    def run(self, user_task: str, max_turns: int = 5, verbose: bool = True) -> Dict[str, Any]:
        """
        执行 Think -> Act -> Observe 循环
        """
        if verbose:
            print(f"\n================ [Study-Harness 任务启动] ================")
            print(f"目标任务：{user_task}\n")

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_task}
        ]

        turn = 0
        final_answer = None
        executed_actions = []

        while turn < max_turns:
            turn += 1
            if verbose:
                print(f"\n--- 【第 {turn} 轮状态机循环心跳】 ---")

            # 1. 【Think 思考阶段】
            if verbose:
                print("  [Think 思考中] 模型正在推理评估当前上下文并决策行动...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                temperature=self.temperature
            )

            msg = response.choices[0].message
            messages.append(msg)

            # 分支判断：无需调用工具，任务达成
            if not msg.tool_calls:
                final_answer = msg.content
                if verbose:
                    print("\n[Finish 任务达成] 模型输出最终总结交付结果：")
                    print(final_answer)
                break

            # 2. 【Act 行动阶段】 与 3. 【Observe 观察阶段】
            for tool_call in msg.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except Exception as e:
                    tool_args = {}

                if verbose:
                    print(f"  [Act 行动发出] 决定调用工具：{tool_name}，参数：{tool_args}")

                # 执行物理工具
                func = self.tool_map.get(tool_name)
                if func:
                    observation = func(**tool_args)
                else:
                    observation = f"错误：未注册的工具函数 {tool_name}"

                executed_actions.append({
                    "turn": turn,
                    "tool": tool_name,
                    "args": tool_args,
                    "observation": observation
                })

                if verbose:
                    print(f"  [Observe 环境观察] 物理事实反馈：{observation}")

                # 将观察结果喂回上下文
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(observation)
                })

        is_completed = final_answer is not None
        if not is_completed and turn >= max_turns:
            if verbose:
                print(f"\n[Stop 安全熔断] 已达到最大轮次预算（{max_turns} 步），强制刹车防死循环。")

        return {
            "completed": is_completed,
            "turns": turn,
            "final_answer": final_answer,
            "actions": executed_actions,
            "messages": messages
        }

def run_harness_loop(user_task: str, max_turns: int = 5) -> Dict[str, Any]:
    """便捷调用入口，完全对齐文章中的独立函数命名"""
    engine = HarnessEngine()
    return engine.run(user_task=user_task, max_turns=max_turns, verbose=True)
