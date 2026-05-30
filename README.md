# Agent Tutorial Demo

这是一个循序渐进的 Agent 教程仓库，按 `demo1` 到 `demo11` 逐步搭建一个越来越完整的 Agent 系统。

如果你是第一次接触 Agent，建议按顺序学习。这个仓库最有价值的地方，不只是把 demo 跑起来，而是能看清楚消息、记忆、工具、规划、工作流、RAG、MCP 这些能力是怎么一层层长出来的。

## 适合谁

- 想从零理解 Agent 基本组成的人
- 已经会调用大模型 API，但不清楚如何做成 Agent 的人
- 想学习 `memory`、`tool calling`、`planning`、`ReAct`、`runtime`、`workflow`、`RAG`、`MCP` 这些核心概念的人
- 想自己写一个轻量 Agent 框架或 coding agent demo 的人

## 环境准备

仓库中的示例主要使用 Python、DeepSeek Chat API、智谱 Embedding SDK、PostgreSQL pgvector 和 MCP Python SDK。

先安装根依赖：

```bash
pip install -r requirements.txt
```

大多数 demo 需要配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

`demo10` 额外需要配置：

```powershell
$env:ZHIPU_API_KEY="你的智谱 API Key"
$env:PGVECTOR_HOST="你的 PostgreSQL 公网访问地址"
$env:PGVECTOR_PASSWORD="你的数据库密码"
```

`demo10` 还需要你自己准备启用了 `pgvector` 扩展的 PostgreSQL 数据库。

## 学习方式

推荐每一节都按这个节奏推进：

1. 先运行当前 demo，感受它能做什么
2. 再读这一节自己的 `README.md`
3. 再看入口文件和关键模块，理解整体流程
4. 最后自己改一个小功能，验证是否真的理解

不要一上来就试图把所有代码一次看懂。最好的学习方式，是按节奏逐步往前推。

## Demo 导航

| Demo | 主题 | 入口 |
| --- | --- | --- |
| `demo1` | 最小 LLM 调用 | [demo1/README.md](demo1/README.md) |
| `demo2` | 多轮对话与短期记忆 | [demo2/README.md](demo2/README.md) |
| `demo3` | Tool Calling 与文件工具 | [demo3/README.md](demo3/README.md) |
| `demo4` | 显式规划与状态推进 | [demo4/README.md](demo4/README.md) |
| `demo5` | ReAct 风格 Agent 循环 | [demo5/README.md](demo5/README.md) |
| `demo6` | 最小 Agent 框架抽象 | [demo6/README.md](demo6/README.md) |
| `demo7` | 简化版 Coding Agent | [demo7/README.md](demo7/README.md) |
| `demo8` | 固定节点编排的 Workflow Agent | [demo8/README.md](demo8/README.md) |
| `demo9` | 带人工审批的 HITL Workflow | [demo9/README.md](demo9/README.md) |
| `demo10` | 基于 pgvector 的 RAG Agent | [demo10/README.md](demo10/README.md) |
| `demo11` | 基于 MCP Server 的工具接入 | [demo11/README.md](demo11/README.md) |

## 推荐学习路线

### 路线一：完全新手

按顺序学习 `demo1` 到 `demo11`。每学完一个 demo，都用自己的话回答：

1. 这一节比上一节多了什么能力
2. 这个能力是靠哪些数据结构和模块实现的
3. 如果让我自己重写，我会保留什么，简化什么

### 路线二：已经会调 LLM API

可以先快速浏览 `demo1`，重点读 `demo2` 到 `demo5`，再把主要精力放在 `demo6` 到 `demo11`。

### 路线三：想写自己的 Agent 框架

推荐重点关注：

1. `demo3`：工具 schema 和执行闭环
2. `demo4`：状态与动作设计
3. `demo5`：ReAct 主循环
4. `demo6`：框架抽象
5. `demo7`：面向代码场景的工具设计
6. `demo8`：节点编排与 workflow 路由
7. `demo9`：人工确认与安全执行边界
8. `demo10`：外部知识库、向量检索与 RAG 问答
9. `demo11`：通过 MCP 接入外部工具生态

## 这套仓库的能力链路

学完这套 demo，通常可以建立下面这条认知链路：

1. LLM 调用本质上只是一次消息请求
2. 多轮对话本质上是维护 `messages`
3. Agent 的“记忆”很多时候先从短期上下文开始
4. Tool Calling 的关键不是“会调工具”，而是“让模型知道什么时候该调”
5. Planning 是把任务拆成可执行步骤
6. ReAct 是“思考-行动-观察”循环
7. 框架化是把 prompt、工具注册、消息存储、运行时循环解耦
8. Coding agent 的核心工作流通常是：先观察，再定位，再修改，再验证
9. Workflow 适合稳定步骤和清晰审计链路
10. HITL 适合高风险动作前的人类确认
11. RAG 让 Agent 在回答前先查资料
12. MCP 让 Agent 更容易接入标准化外部工具

## 详细文档在哪里

顶层 README 现在只保留总览和导航。每一节的完整讲解、关键模块、运行方式、学习重点和建议练习，都已经拆到对应的 `demoN/README.md` 里。

你可以直接从上面的 demo 导航进入任意一节继续看。
