[返回首页](../README.md) | [上一节：demo2](../demo2/README.md) | [下一节：demo4](../demo4/README.md)

# demo3：Tool Calling Demo

这一节开始真正进入 Agent 的关键能力：让模型不只“回答”，还可以“做事”。

## 本节目标

- 理解工具 schema 是怎么描述给模型的
- 学会执行模型发起的工具调用
- 理解工具结果如何反馈回模型，形成闭环

## 入口文件

- [tool_demo.py](tool_demo.py)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo3/tool_demo.py
```

## 本节新增能力

- 定义 `tools`
- 让模型自动决定是否调用工具
- 执行本地工具函数
- 把工具执行结果再反馈给模型，让模型生成最终回复
- 限制工具只能写入 `demo3/generated_files`

## 内置工具

- `create_text_file`

## 学习重点

- `build_tools()`：工具 schema 是怎么描述给模型的
- `execute_tool_call()`：如何解析模型生成的 JSON 参数
- `create_text_file()`：如何做安全路径限制
- `run_agent_turn()`：工具调用和模型回复如何形成闭环

这一节非常关键，因为它会让你看到一个事实：Agent 之所以“像代理”，不是因为它会聊天，而是因为它有了可以执行的动作空间。

## 建议练习

- 让它生成一个 Markdown 文件
- 故意给出复杂一点的内容，观察工具参数是否容易出错
- 尝试新增一个只读工具，比如读取文件内容

## 与上一节相比多了什么

`demo2` 里模型只能说，`demo3` 里模型第一次具备了“行动能力”。从这一步开始，Agent 才真正从聊天程序走向“可执行任务”的系统。

[返回首页](../README.md) | [上一节：demo2](../demo2/README.md) | [下一节：demo4](../demo4/README.md)
