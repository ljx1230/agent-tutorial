# Agent Tutorial Demo

这是一个循序渐进的 Agent 教程仓库，按 `demo1` 到 `demo8` 逐步搭建一个越来越完整的 Agent 系统。

整个仓库的设计思路很清晰：

- `demo1` 先学最基础的 LLM 调用
- `demo2` 加上多轮对话和短期记忆
- `demo3` 引入工具调用
- `demo4` 演示显式规划
- `demo5` 进入 ReAct 风格 Agent
- `demo6` 把前面的能力抽象成一个最小框架
- `demo7` 用这个框架做一个简化版 coding agent
- `demo8` 再往前一步，引入固定节点和路由的 workflow agent

如果你是第一次接触 Agent，建议严格按顺序学习，不要直接跳到后面的 demo。这个仓库最有价值的地方，不只是“跑起来”，而是能看清楚 Agent 的能力是怎么一层层长出来的。

## 适合谁

这个仓库适合以下几类同学：

- 想从零理解 Agent 基本组成的人
- 已经会调用大模型 API，但不清楚如何做成 Agent 的人
- 想学习 `memory`、`tool calling`、`planning`、`ReAct`、`runtime` 这些核心概念的人
- 想自己写一个轻量 Agent 框架或 coding agent demo 的人

## 你会学到什么

学完这套 demo，通常可以建立下面这条认知链路：

1. LLM 调用本质上只是一次消息请求
2. 多轮对话本质上是维护 `messages`
3. Agent 的“记忆”很多时候先从短期上下文开始
4. Tool Calling 的关键不是“会调工具”，而是“让模型知道什么时候该调”
5. Planning 是把任务拆成可执行步骤
6. ReAct 是“思考-行动-观察”循环
7. 框架化是把 prompt、工具注册、消息存储、运行时循环解耦
8. Coding agent 的核心工作流通常是：先观察，再定位，再修改，再验证

## 环境准备

仓库中的示例主要使用 Python 和 DeepSeek Chat API。

先安装依赖：

```bash
pip install requests
```

然后在 PowerShell 中配置环境变量：

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

大多数 demo 都可以直接运行对应入口文件，例如：

```bash
python demo1/hello_world.py
python demo2/memory_demo.py
python demo3/tool_demo.py
python demo4/planning_demo.py
python demo5/react_demo.py
python demo6/framework_demo.py
python demo7/coding_agent_demo.py
python demo8/workflow_demo.py
```

## 仓库结构

```text
demo1/  Hello World：最小 LLM 调用
demo2/  Memory：多轮对话与短期记忆
demo3/  Tool Calling：文件创建工具
demo4/  Planning：显式步骤规划
demo5/  ReAct：思考-行动-观察循环
demo6/  Framework：最小 Agent 框架
demo7/  Coding Agent：受限工作区内的代码代理
demo8/  Workflow Agent：固定节点编排的工作流代理
```

## Demo 逐个介绍

### demo1：Hello World

入口文件：[demo1/hello_world.py](D:\code\ai\agent-tutorial-public\demo1\hello_world.py)

这是整个教程的起点，目标只有一个：把一次最基础的大模型调用跑通。

这个 demo 展示了：

- 如何组织 `system` 和 `user` 消息
- 如何通过 `requests` 请求 DeepSeek Chat API
- 如何读取模型返回的 `choices[0].message.content`
- 如何查看一次请求的 token 使用情况

学习时重点看：

- `build_messages()`：消息是怎么组织的
- `call_llm()`：一次 API 请求的最小必要参数有哪些
- `main()`：如何从环境变量中读取 API Key

建议你在这一节动手做的事：

- 改写 `system prompt`
- 改写 `user prompt`
- 试着调 `temperature` 和 `max_tokens`
- 打印完整返回 JSON，理解响应结构

这一节的核心不是 Agent，而是先把“模型调用”这块地基打稳。

### demo2：Memory Demo

入口文件：[demo2/memory_demo.py](D:\code\ai\agent-tutorial-public\demo2\memory_demo.py)

这一节开始进入“像 Agent 一点”的形态：程序不再只做一次调用，而是进入交互循环，并保留对话历史。

这个 demo 展示了：

- 如何维护 `messages` 列表
- 如何把上一轮的 `assistant` 回复也放回上下文
- 如何通过裁剪消息列表模拟“短期记忆”
- 为什么会话越长，token 成本越高

学习时重点看：

- `create_system_message()`：持续约束助手身份
- `trim_messages()`：如何只保留最近几轮消息
- `main()` 中的 while 循环：消息是如何追加和回写的

建议你重点理解：

- 多轮对话不神秘，本质上就是反复把历史消息一起发给模型
- 所谓 memory，在早期 demo 里主要就是“保留上下文”
- 不做裁剪，消息会越来越长，成本和延迟都会上升

如果你看懂了这一节，就已经理解了很多聊天型 Agent 的最小实现方式。

### demo3：Tool Calling Demo

入口文件：[demo3/tool_demo.py](D:\code\ai\agent-tutorial-public\demo3\tool_demo.py)

这一节开始真正进入 Agent 的关键能力：让模型不只“回答”，还可以“做事”。

这个 demo 展示了：

- 如何定义 `tools`
- 如何让模型自动决定是否调用工具
- 如何执行本地工具函数
- 如何把工具执行结果再反馈给模型，让模型生成最终回复
- 如何限制工具只能写入 `demo3/generated_files`

内置工具：

- `create_text_file`

学习时重点看：

- `build_tools()`：工具 schema 是怎么描述给模型的
- `execute_tool_call()`：如何解析模型生成的 JSON 参数
- `create_text_file()`：如何做安全路径限制
- `run_agent_turn()`：工具调用和模型回复如何形成闭环

这一节非常关键，因为它会让你看到一个事实：

Agent 之所以“像代理”，不是因为它会聊天，而是因为它有了可以执行的动作空间。

建议练习：

- 让它生成一个 markdown 文件
- 故意给出复杂一点的内容，观察工具参数是否容易出错
- 尝试新增一个只读工具，比如读取文件内容

### demo4：Planning Demo

入口文件：[demo4/planning_demo.py](D:\code\ai\agent-tutorial-public\demo4\planning_demo.py)

这一节把“先做什么、后做什么”显式化，让模型不再直接冲着结果输出，而是先决定下一步动作。

这个 demo 展示了：

- 如何把任务拆成多个步骤
- 如何维护结构化状态 `state`
- 如何让模型只返回 JSON 决策
- 如何通过动作枚举控制执行流程
- 如何在 `decide_path -> draft_content -> create_file -> finish` 之间推进任务

学习时重点看：

- `create_system_message()`：如何严格约束输出格式和动作集合
- `build_state_message()`：如何把当前状态整理给模型
- `call_planner()`：如何把“规划器”当作一个只做决策的模型调用
- `run_task_agent()`：如何在程序侧接管执行流程

这一节最值得体会的，是“模型负责决策，程序负责执行”的边界感。

和 `demo3` 相比，这一节的模型自由度更低，但任务推进更稳定，也更适合讲清楚 Agent 的内部执行过程。

### demo5：ReAct Demo

入口文件：[demo5/react_demo.py](D:\code\ai\agent-tutorial-public\demo5\react_demo.py)

关键模块：

- [demo5/agent.py](D:\code\ai\agent-tutorial-public\demo5\agent.py)
- [demo5/tools.py](D:\code\ai\agent-tutorial-public\demo5\tools.py)
- [demo5/state.py](D:\code\ai\agent-tutorial-public\demo5\state.py)

这一节从“显式规划”过渡到更常见的 ReAct 风格循环。

这个 demo 展示了：

- 模型如何根据上下文自行决定是否继续调用工具
- `messages` 和记忆仍然保留
- 额外引入了 `state` 作为结构化任务状态
- 工具从单一写文件扩展为“创建、读取、列出文件”
- 通过循环多次观察工具结果，再决定下一步

内置工具：

- `create_text_file`
- `read_text_file`
- `list_files`

学习时重点看：

- `run_react_agent()`：主循环如何驱动整个 Agent
- `build_runtime_messages()`：为什么既需要 `messages`，也需要 `state`
- `update_state_from_tool_result()`：工具结果如何反哺状态

这节是一个很好的分水岭。看到这里，你会开始理解：

- 仅靠固定步骤也能做事，但灵活性有限
- 仅靠自由 Tool Calling 又可能不够稳
- ReAct 是在“灵活”和“可控”之间找平衡

建议练习：

- 让 Agent 先生成文件，再自己读出来检查
- 让 Agent 列出已有文件，再挑一个继续修改或总结

### demo6：Framework Demo

入口文件：[demo6/framework_demo.py](D:\code\ai\agent-tutorial-public\demo6\framework_demo.py)

框架目录：

- [demo6/framework/__init__.py](D:\code\ai\agent-tutorial-public\demo6\framework\__init__.py)
- [demo6/framework/runtime.py](D:\code\ai\agent-tutorial-public\demo6\framework\runtime.py)
- [demo6/framework/tool_registry.py](D:\code\ai\agent-tutorial-public\demo6\framework\tool_registry.py)
- [demo6/framework/message_store.py](D:\code\ai\agent-tutorial-public\demo6\framework\message_store.py)
- [demo6/framework/decorators.py](D:\code\ai\agent-tutorial-public\demo6\framework\decorators.py)

工具模块：

- [demo6/builtin_tools.py](D:\code\ai\agent-tutorial-public\demo6\builtin_tools.py)

这一节的重点不再是“再多一个 Agent 能力”，而是把前面几节的通用逻辑抽象出来。

这个 demo 展示了：

- 如何封装 `ToolRegistry`
- 如何封装 `MessageStore`
- 如何通过 `@tool` 装饰器声明工具
- 如何通过 `create_runtime(...)` 快速组装一个最小 Agent Runtime
- 如何让工具通过 `context_updates` 回写共享上下文

这一节是从“写 demo”走向“写框架”的开始。

你可以把它理解为：前五节都在造概念，第六节开始整理工程结构。

建议按下面顺序读代码：

1. 先看 `framework_demo.py`
2. 再看 `demo6/framework/__init__.py`
3. 再看 `tool_registry.py` 和 `decorators.py`
4. 再看 `runtime.py`
5. 最后回头看 `builtin_tools.py`

学习目标不是记住所有细节，而是理解下面这几个抽象层：

- 模型调用层
- 工具注册层
- 消息存储层
- Runtime 执行层
- 业务工具层

### demo7：Coding Agent Demo

入口文件：[demo7/coding_agent_demo.py](D:\code\ai\agent-tutorial-public\demo7\coding_agent_demo.py)

关键模块：

- [demo7/coding_runtime.py](D:\code\ai\agent-tutorial-public\demo7\coding_runtime.py)
- [demo7/coding_tools.py](D:\code\ai\agent-tutorial-public\demo7\coding_tools.py)
- [demo7/project_workspace/README.md](D:\code\ai\agent-tutorial-public\demo7\project_workspace\README.md)

这一节把前面搭好的框架用在一个更具体的场景里：代码分析与代码修改。

这个 demo 展示了：

- 如何把 Agent 的工作范围限制在 `demo7/project_workspace`
- 如何给 coding agent 提供“观察型工具”和“修改型工具”
- 如何让 Agent 先搜索，再阅读，再替换，再写回
- 如何做更安全的文本替换，例如 `expected_occurrences`

内置工具大致分两类：

- 观察型工具：`list_files`、`search_text`、`search_files_by_name`、`read_text_file`
- 修改型工具：`replace_text_in_file`、`write_text_file`

这个设计非常适合教学，因为它把 coding agent 的真实工作流讲得很直白：

1. 先看目录
2. 再搜文件或关键字
3. 再读具体内容
4. 最后做精确修改

示例工作区在这里：

- [demo7/project_workspace/app.py](D:\code\ai\agent-tutorial-public\demo7\project_workspace\app.py)
- [demo7/project_workspace/settings.py](D:\code\ai\agent-tutorial-public\demo7\project_workspace\settings.py)
- [demo7/project_workspace/utils.py](D:\code\ai\agent-tutorial-public\demo7\project_workspace\utils.py)

建议你尝试 `project_workspace/README.md` 里给出的任务，例如：

- 找到 `greet_user`，给空名字增加更友好的处理
- 把 `DEFAULT_THEME` 从 `light` 改成 `dark`
- 定位某段业务逻辑并让 Agent 总结它的作用

如果你能看懂这一节，基本就已经具备自己做一个小型 coding agent 原型的能力了。

### demo8：Workflow Agent Demo

入口文件：[demo8/workflow_demo.py](D:\code\ai\agent-tutorial-public\demo8\workflow_demo.py)

关键模块：

- [demo8/framework/workflow.py](D:\code\ai\agent-tutorial-public\demo8\framework\workflow.py)
- [demo8/framework/node.py](D:\code\ai\agent-tutorial-public\demo8\framework\node.py)
- [demo8/framework/context.py](D:\code\ai\agent-tutorial-public\demo8\framework\context.py)
- [demo8/nodes.py](D:\code\ai\agent-tutorial-public\demo8\nodes.py)
- [demo8/tools.py](D:\code\ai\agent-tutorial-public\demo8\tools.py)

这一节继续沿着 `demo6`、`demo7` 往前走，但重点从“通用 runtime”切到“固定工作流编排”。

这个 demo 展示了：

- 如何把任务拆成一组固定节点
- 如何让节点通过 `action` 决定下一跳
- 如何把 `classify -> inspect -> plan -> apply -> verify -> report` 串成一条工作流
- 如何把 workflow 能力和业务节点实现分层
- 如何在代码修改任务里显式加入“验证”步骤

`demo8` 里的典型工作流是：

1. `ClassifyNode` 先判断这是“总结类任务”还是“修改类任务”
2. `InspectNode` 先查看目录、文件快照和搜索结果
3. `PlanNode` 产出一个精确修改计划
4. `ApplyNode` 执行修改
5. `VerifyNode` 再读取文件确认变更结果
6. `ReportNode` 输出最终总结

和 `demo7` 相比，这一节更强调：

- 任务流转是显式节点，不只是自由循环
- 每个节点职责更单一，更适合扩展和调试
- 对于需要稳定步骤、清晰审计链路的任务，workflow 往往比自由 Agent 更容易控

示例工作区在这里：

- [demo8/project_workspace/README.md](D:\code\ai\agent-tutorial-public\demo8\project_workspace\README.md)
- [demo8/project_workspace/app.py](D:\code\ai\agent-tutorial-public\demo8\project_workspace\app.py)
- [demo8/project_workspace/settings.py](D:\code\ai\agent-tutorial-public\demo8\project_workspace\settings.py)
- [demo8/project_workspace/utils.py](D:\code\ai\agent-tutorial-public\demo8\project_workspace\utils.py)

建议你用这一节重点体会两个问题：

- 什么场景适合“自由 agent”
- 什么场景更适合“固定 workflow”

如果 `demo7` 教你的是“像 coding agent 一样工作”，那么 `demo8` 教你的就是“把这套工作方式编排成可预测的流程”。

## 推荐学习路线

### 路线一：完全新手

按顺序学习：

1. `demo1`：先跑通 API
2. `demo2`：理解消息历史
3. `demo3`：理解工具调用闭环
4. `demo4`：理解规划和状态
5. `demo5`：理解 ReAct 主循环
6. `demo6`：理解框架抽象
7. `demo7`：理解真实场景落地
8. `demo8`：理解 workflow 编排和显式验证

每学完一个 demo，都建议做两件事：

- 用自己的话总结“这一节比上一节多了什么”
- 自己改一个小功能，不要只停留在运行

### 路线二：已经会调 LLM API

如果你已经熟悉基础 API 调用，可以这样学：

1. 快速浏览 `demo1`
2. 重点读 `demo2` 到 `demo5`
3. 把主要精力放在 `demo6`、`demo7` 和 `demo8`

这种路线更适合已经会写 prompt、会调接口，但还没形成 Agent 系统思维的人。

### 路线三：想写自己的 Agent 框架

推荐重点看这几个部分：

1. `demo3`：工具 schema 和执行闭环
2. `demo4`：状态与动作设计
3. `demo5`：ReAct 主循环
4. `demo6`：框架抽象
5. `demo7`：面向代码场景的工具设计
6. `demo8`：节点编排与 workflow 路由

你的关注点应该放在这些问题上：

- Tool schema 怎么定义更清楚
- Runtime 该怎么组织
- 工具结果怎么回写上下文
- 如何给模型足够的动作空间，同时又不失控
- 如何做安全边界限制

## 每个阶段建议重点思考的问题

### 学完 demo1 后

- 一次聊天请求最少需要什么
- `system` 和 `user` 的职责分别是什么

### 学完 demo2 后

- 为什么说“记忆”很多时候先是消息历史
- 为什么要做消息裁剪

### 学完 demo3 后

- 模型什么时候该回答，什么时候该调用工具
- 工具参数为什么必须结构化

### 学完 demo4 后

- 什么情况下适合显式规划
- 状态机式 Agent 和自由式 Agent 的差别是什么

### 学完 demo5 后

- `messages` 和 `state` 为什么可以并存
- ReAct 和固定规划相比，各自优缺点是什么

### 学完 demo6 后

- 什么逻辑适合抽到框架层
- 什么逻辑应该留在业务工具层

### 学完 demo7 后

- coding agent 为什么必须强调“先观察后修改”
- 为什么代码修改工具需要更强的安全约束

### 学完 demo8 后

- workflow 节点和通用 agent loop 的取舍是什么
- 为什么有些任务需要单独的 verify 节点

## 建议的动手练习

如果你想真正学会，建议按这个顺序自己改：

1. 在 `demo1` 中替换 prompt，输出另一种风格的回答
2. 在 `demo2` 中把记忆轮数改大改小，观察行为变化
3. 在 `demo3` 中新增一个“读取文件”工具
4. 在 `demo4` 中新增一个动作，比如“先总结需求”
5. 在 `demo5` 中让 Agent 支持“先创建再读取再总结”
6. 在 `demo6` 中新增一个你自己的 `@tool`
7. 在 `demo7` 中增加一个“只做分析、不做修改”的审查型工具
8. 在 `demo8` 中新增一个节点，比如“review patch”或“risk check”

## 如何用这份仓库来学习

一个很有效的方法是：

1. 先运行当前 demo，感受它能做什么
2. 再只读入口文件，理解整体流程
3. 再读关键函数，搞清楚状态怎么流转
4. 最后自己改一处功能，验证是否真的理解

不要一上来就试图把所有代码一次看懂。这个仓库是按教学节奏组织的，最好的学习方式也是按节奏推进。

建议你每一节都回答这三个问题：

1. 这一节新增了什么能力
2. 这个能力是靠哪些数据结构实现的
3. 如果让我自己重写，我会保留什么，简化什么

## 总结

这套 demo 的价值在于，它没有一开始就把 Agent 包装成一个黑盒框架，而是把核心机制拆开给你看：

- 消息
- 记忆
- 工具
- 规划
- 状态
- 循环
- 框架
- 工作流编排
- 场景化落地

如果你按顺序学完，并且每一节都自己改过一点代码，基本就能从“会调用模型”进阶到“会设计一个最小可用 Agent 系统”。
