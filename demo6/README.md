[返回首页](../README.md) | [上一节：demo5](../demo5/README.md) | [下一节：demo7](../demo7/README.md)

# demo6：Framework Demo

这一节的重点不再是“再多一个 Agent 能力”，而是把前面几节的通用逻辑抽象出来。

## 本节目标

- 理解一个最小 Agent 框架通常会拆成哪些层
- 学会把工具注册、消息存储、运行时循环解耦
- 为后面的 coding agent、workflow、MCP 接入打好框架基础

## 入口文件

- [framework_demo.py](framework_demo.py)

## 关键模块

- [framework/__init__.py](framework/__init__.py)
- [framework/runtime.py](framework/runtime.py)
- [framework/tool_registry.py](framework/tool_registry.py)
- [framework/message_store.py](framework/message_store.py)
- [framework/decorators.py](framework/decorators.py)
- [builtin_tools.py](builtin_tools.py)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo6/framework_demo.py
```

## 本节新增能力

- 封装 `ToolRegistry`
- 封装 `MessageStore`
- 通过 `@tool` 装饰器声明工具
- 通过 `create_runtime(...)` 快速组装一个最小 Agent Runtime
- 让工具通过 `context_updates` 回写共享上下文

## 建议阅读顺序

1. 先看 [framework_demo.py](framework_demo.py)
2. 再看 [framework/__init__.py](framework/__init__.py)
3. 再看 [framework/tool_registry.py](framework/tool_registry.py) 和 [framework/decorators.py](framework/decorators.py)
4. 再看 [framework/runtime.py](framework/runtime.py)
5. 最后回头看 [builtin_tools.py](builtin_tools.py)

## 学习重点

这一节的学习目标不是记住所有细节，而是理解下面这几个抽象层：

- 模型调用层
- 工具注册层
- 消息存储层
- Runtime 执行层
- 业务工具层

你也可以把它理解为：前五节都在造概念，第六节开始整理工程结构。

## 建议练习

- 新增一个你自己的 `@tool`
- 给 Runtime 增加一个更严格的循环次数限制
- 观察 `MessageStore` 和 `ToolRegistry` 如果换实现，会影响哪些地方

## 与上一节相比多了什么

`demo5` 还是“把逻辑写在 demo 里”，`demo6` 开始把这些通用能力抽成框架。后面的 `demo7`、`demo8`、`demo9` 和 `demo11`，都会直接复用这里的基础设施。

[返回首页](../README.md) | [上一节：demo5](../demo5/README.md) | [下一节：demo7](../demo7/README.md)
