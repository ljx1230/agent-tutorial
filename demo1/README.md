[返回首页](../README.md) | [下一节：demo2](../demo2/README.md)

# demo1：Hello World

这是整个教程的起点，目标只有一个：把一次最基础的大模型调用跑通。

## 本节目标

- 理解一次最小 LLM 调用需要哪些消息和参数
- 学会用 `requests` 请求 DeepSeek Chat API
- 看懂模型响应里的内容和 token 使用情况

## 入口文件

- [hello_world.py](hello_world.py)

## 运行方式

先确保已经安装根依赖，并配置好：

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

然后运行：

```bash
python demo1/hello_world.py
```

## 本节新增能力

- 组织 `system` 和 `user` 消息
- 发起一次完整的 Chat Completions 风格请求
- 读取 `choices[0].message.content`
- 查看一次请求的 token 使用信息

## 学习重点

- `build_messages()`：消息是怎么组织的
- `call_llm()`：一次 API 请求的最小必要参数有哪些
- `main()`：如何从环境变量中读取 API Key

这一节的核心不是 Agent，而是先把“模型调用”这块地基打稳。

## 建议练习

- 改写 `system prompt`
- 改写 `user prompt`
- 试着调 `temperature` 和 `max_tokens`
- 打印完整返回 JSON，理解响应结构

## 和后续章节的关系

这一节还没有记忆、工具和循环。后面所有 demo，都会建立在这里这套“消息输入 -> 模型调用 -> 读取响应”的最小闭环上。

[返回首页](../README.md) | [下一节：demo2](../demo2/README.md)
