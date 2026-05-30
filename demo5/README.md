[返回首页](../README.md) | [上一节：demo4](../demo4/README.md) | [下一节：demo6](../demo6/README.md)

# demo5：ReAct Demo

这一节从“显式规划”过渡到更常见的 ReAct 风格循环。

## 本节目标

- 理解 ReAct 如何在灵活性和可控性之间找平衡
- 学会同时维护 `messages` 和结构化 `state`
- 看懂一个带多工具、多轮观察的 Agent 主循环

## 入口文件

- [react_demo.py](react_demo.py)

## 关键模块

- [agent.py](agent.py)
- [tools.py](tools.py)
- [state.py](state.py)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo5/react_demo.py
```

## 本节新增能力

- 模型根据上下文自行决定是否继续调用工具
- `messages` 和记忆仍然保留
- 额外引入 `state` 作为结构化任务状态
- 工具从单一写文件扩展为“创建、读取、列出文件”
- 通过循环多次观察工具结果，再决定下一步

## 内置工具

- `create_text_file`
- `read_text_file`
- `list_files`

## 学习重点

- `run_react_agent()`：主循环如何驱动整个 Agent
- `build_runtime_messages()`：为什么既需要 `messages`，也需要 `state`
- `update_state_from_tool_result()`：工具结果如何反哺状态

这节是一个很好的分水岭。看到这里，你会开始理解：

- 仅靠固定步骤也能做事，但灵活性有限
- 仅靠自由 Tool Calling 又可能不够稳
- ReAct 是在“灵活”和“可控”之间找平衡

## 建议练习

- 让 Agent 先生成文件，再自己读出来检查
- 让 Agent 列出已有文件，再挑一个继续修改或总结
- 尝试增加一个工具，观察主循环是否还能稳定工作

## 与上一节相比多了什么

`demo4` 更像显式状态机，`demo5` 则进入更常见的自由循环式 Agent。它没有完全放弃结构，而是把结构藏进运行时和状态里。

[返回首页](../README.md) | [上一节：demo4](../demo4/README.md) | [下一节：demo6](../demo6/README.md)
