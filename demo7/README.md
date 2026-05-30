[返回首页](../README.md) | [上一节：demo6](../demo6/README.md) | [下一节：demo8](../demo8/README.md)

# demo7：Coding Agent Demo

这一节把前面搭好的框架用在一个更具体的场景里：代码分析与代码修改。

## 本节目标

- 理解 coding agent 为什么必须强调“先观察后修改”
- 学会为代码任务设计观察型工具和修改型工具
- 理解受限工作区、安全替换和最小改动的重要性

## 入口文件

- [coding_agent_demo.py](coding_agent_demo.py)

## 关键模块

- [coding_runtime.py](coding_runtime.py)
- [coding_tools.py](coding_tools.py)
- [project_workspace/README.md](project_workspace/README.md)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo7/coding_agent_demo.py
```

## 本节新增能力

- 把 Agent 的工作范围限制在 `demo7/project_workspace`
- 提供“观察型工具”和“修改型工具”
- 让 Agent 先搜索，再阅读，再替换，再写回
- 做更安全的文本替换，例如 `expected_occurrences`

## 内置工具

观察型工具：

- `list_files`
- `search_text`
- `search_files_by_name`
- `read_text_file`

修改型工具：

- `replace_text_in_file`
- `write_text_file`

## 学习重点

这个设计非常适合教学，因为它把 coding agent 的真实工作流讲得很直白：

1. 先看目录
2. 再搜文件或关键字
3. 再读具体内容
4. 最后做精确修改

建议重点看：

- `coding_runtime.py`：Runtime 如何组织“先观察后修改”的行为
- `coding_tools.py`：代码工具为什么要比普通文件工具更谨慎
- `project_workspace`：示例任务是怎么设计出来的

## 示例工作区

- [project_workspace/app.py](project_workspace/app.py)
- [project_workspace/settings.py](project_workspace/settings.py)
- [project_workspace/utils.py](project_workspace/utils.py)
- [project_workspace/README.md](project_workspace/README.md)

## 建议练习

- 找到 `greet_user`，给空名字增加更友好的处理
- 把 `DEFAULT_THEME` 从 `light` 改成 `dark`
- 定位某段业务逻辑并让 Agent 总结它的作用

## 与上一节相比多了什么

`demo6` 提供的是通用框架，`demo7` 开始把它落到“代码任务”这个具体场景里。看懂这一节，你基本就具备自己做一个小型 coding agent 原型的能力了。

[返回首页](../README.md) | [上一节：demo6](../demo6/README.md) | [下一节：demo8](../demo8/README.md)
