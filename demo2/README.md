[返回首页](../README.md) | [上一节：demo1](../demo1/README.md) | [下一节：demo3](../demo3/README.md)

# demo2：Memory Demo

这一节开始进入“像 Agent 一点”的形态：程序不再只做一次调用，而是进入交互循环，并保留对话历史。

## 本节目标

- 理解多轮对话为什么本质上是维护 `messages`
- 学会把历史轮次不断放回上下文
- 理解短期记忆和消息裁剪的意义

## 入口文件

- [memory_demo.py](memory_demo.py)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo2/memory_demo.py
```

## 本节新增能力

- 维护 `messages` 列表
- 把上一轮的 `assistant` 回复也放回上下文
- 通过裁剪消息列表模拟“短期记忆”
- 观察会话变长后 token 成本和延迟的变化

## 学习重点

- `create_system_message()`：持续约束助手身份
- `trim_messages()`：如何只保留最近几轮消息
- `main()` 中的 while 循环：消息是如何追加和回写的

建议重点理解这几个事实：

- 多轮对话不神秘，本质上就是反复把历史消息一起发给模型
- 所谓 memory，在早期 demo 里主要就是“保留上下文”
- 不做裁剪，消息会越来越长，成本和延迟都会上升

## 建议练习

- 把保留轮数调大调小，观察行为变化
- 给 system message 增加更强的人设约束
- 让程序打印每轮发送给模型的消息数量

## 与上一节相比多了什么

`demo1` 只演示一次调用，`demo2` 开始引入“持续会话”这个 Agent 最常见的外壳。看懂这一节，你就已经理解了很多聊天型 Agent 的最小实现方式。

[返回首页](../README.md) | [上一节：demo1](../demo1/README.md) | [下一节：demo3](../demo3/README.md)
