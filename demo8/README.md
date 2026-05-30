[返回首页](../README.md) | [上一节：demo7](../demo7/README.md) | [下一节：demo9](../demo9/README.md)

# demo8：Workflow Agent Demo

这一节继续沿着 `demo6`、`demo7` 往前走，但重点从“通用 runtime”切到“固定工作流编排”。

## 本节目标

- 理解什么场景适合用固定 workflow 而不是自由循环 Agent
- 学会把任务拆成固定节点和显式路由
- 理解验证节点在稳定任务流中的价值

## 入口文件

- [workflow_demo.py](workflow_demo.py)

## 关键模块

- [framework/workflow.py](framework/workflow.py)
- [framework/node.py](framework/node.py)
- [framework/context.py](framework/context.py)
- [nodes.py](nodes.py)
- [tools.py](tools.py)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo8/workflow_demo.py
```

## 本节新增能力

- 把任务拆成一组固定节点
- 让节点通过 `action` 决定下一跳
- 把 `classify -> inspect -> plan -> apply -> verify -> report` 串成一条工作流
- 把 workflow 能力和业务节点实现分层
- 在代码修改任务里显式加入“验证”步骤
- 把框架层上下文抽象成更通用的 `WorkflowContext`

## 典型工作流

1. `ClassifyNode` 先判断这是“总结类任务”还是“修改类任务”
2. `InspectNode` 先查看目录、文件快照和搜索结果
3. `PlanNode` 产出一个精确修改计划
4. `ApplyNode` 执行修改
5. `VerifyNode` 再读取文件确认变更结果
6. `ReportNode` 输出最终总结

## 学习重点

和 `demo7` 相比，这一节更强调：

- 任务流转是显式节点，不只是自由循环
- 每个节点职责更单一，更适合扩展和调试
- 对于需要稳定步骤、清晰审计链路的任务，workflow 往往比自由 Agent 更容易控

## 示例工作区

- [project_workspace/app.py](project_workspace/app.py)
- [project_workspace/settings.py](project_workspace/settings.py)
- [project_workspace/utils.py](project_workspace/utils.py)
- [project_workspace/README.md](project_workspace/README.md)

## 建议练习

- 在现有流程中新增一个节点，比如 `risk check`
- 对比“自由 agent”与“固定 workflow”在同一个任务上的表现差异
- 试着让 `VerifyNode` 多做一步结果总结

## 与上一节相比多了什么

`demo7` 教你的是“像 coding agent 一样工作”，`demo8` 教你的就是“把这套工作方式编排成可预测的流程”。

[返回首页](../README.md) | [上一节：demo7](../demo7/README.md) | [下一节：demo9](../demo9/README.md)
