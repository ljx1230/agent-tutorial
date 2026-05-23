from __future__ import annotations

import json
from typing import Any

from demo6.framework import AgentRuntime

from demo7.config import MAX_AGENT_LOOPS, WORKSPACE_DIR


class CodingAgentRuntime(AgentRuntime):
    """
    基于 demo6 框架扩展出来的最小本地 coding agent runtime。

    这里的重点是：
    - 不复制第六课框架
    - 只通过覆写少数方法做“场景化定制”
    """

    def __init__(self, api_key: str, tool_registry) -> None:
        super().__init__(
            api_key=api_key,
            tool_registry=tool_registry,
            max_loops=MAX_AGENT_LOOPS,
            system_message=self.create_coding_system_message(),
        )

    def create_coding_system_message(self) -> dict[str, str]:
        """为 coding agent 定制系统提示词。"""
        return {
            "role": "system",
            "content": (
                "你是一个最小本地 coding agent。"
                "你的工作是先观察代码，再决定是否修改代码。"
                "优先使用 list_files、search_text、search_files_by_name、read_text_file 来定位相关代码。"
                "只有在你已经阅读并确认目标文件后，才进行修改。"
                "做小规模、精确的修改时优先使用 replace_text_in_file。"
                "如果需要创建或重写完整文件，使用 write_text_file。"
                "不要声称代码已修改，除非你已经看到了真实工具结果。"
                "当前工作区只允许在 demo7/project_workspace 中。"
                "回答使用简洁清晰的中文。"
            ),
        }

    def create_state(self, goal: str) -> dict[str, Any]:
        """
        创建 coding agent 的任务状态。

        和 demo6 的通用 runtime 相比，这里只多了一点点项目上下文：
        把工作区路径放进 shared_context。
        """
        state = super().create_state(goal)
        state["shared_context"] = {
            "workspace_dir": str(WORKSPACE_DIR),
        }
        return state

    def build_runtime_message(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        为 coding agent 定制运行时调度消息。

        这里和第六课最大的区别是：
        提示词不再泛泛地说“完成任务”，而是明确要求先观察代码、再做修改。
        """
        return {
            "role": "user",
            "content": (
                "你正在处理一个本地 Python 项目工作区。\n"
                f"- goal: {state.get('goal')!r}\n"
                f"- workspace_dir: {state.get('shared_context', {}).get('workspace_dir')!r}\n"
                f"- shared_context: {json.dumps(state.get('shared_context', {}), ensure_ascii=False)}\n"
                f"- last_tool_name: {state.get('last_tool_name')!r}\n"
                f"- last_tool_result: {json.dumps(state.get('last_tool_result'), ensure_ascii=False)}\n"
                f"- completed: {state.get('completed')!r}\n"
                f"- loop_count: {state.get('loop_count')!r}\n"
                "你的目标是完成一个小规模、可验证的代码任务。"
                "在修改前，先定位并读取相关代码。"
                "如果任务已完成，直接给出最终答复。"
            ),
        }
