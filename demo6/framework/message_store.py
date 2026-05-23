from __future__ import annotations

from typing import Any


class MessageStore:
    """
    管理会话消息和历史裁剪。

    第六课的目标之一，是把“消息管理”从 Agent 运行时里拆出来。
    """

    def __init__(self, max_turns: int) -> None:
        self.max_turns = max_turns
        self.messages: list[dict[str, Any]] = []

    def append(self, message: dict[str, Any]) -> None:
        # 所有消息最终都通过这里进入存储，
        # 这样裁剪逻辑就不会散落在各个调用方里。
        self.messages.append(message)
        self.trim()

    def extend(self, new_messages: list[dict[str, Any]]) -> None:
        # 主要给“批量回写消息”的场景留接口，
        # 虽然当前 demo 用得不多，但作为框架层抽象更完整。
        self.messages.extend(new_messages)
        self.trim()

    def trim(self) -> None:
        """
        裁剪最近若干轮消息。

        在带工具的 ReAct 循环里，一次完整交互经常接近：
        user -> assistant(tool_call) -> tool -> assistant
        所以这里按每轮约 4 条消息估算。
        """
        max_message_count = self.max_turns * 4
        if len(self.messages) > max_message_count:
            self.messages = self.messages[-max_message_count:]

    def snapshot(self) -> list[dict[str, Any]]:
        """返回当前消息快照。"""
        return list(self.messages)
