[返回首页](../README.md) | [上一节：demo8](../demo8/README.md) | [下一节：demo10](../demo10/README.md)

# demo9：HITL Workflow Demo

这一节是在 `demo8` 的 workflow 基础上继续往前推进，核心主题是 Human-in-the-Loop。

## 本节目标

- 理解什么情况下需要在 Agent 流程中加入人工确认
- 学会把“修改计划”和“真正落盘”拆成两个阶段
- 理解可用 Agent 系统为什么很多时候不是更自动，而是更可控

## 入口文件

- [hitl_demo.py](hitl_demo.py)

## 关键模块

- [hitl_context.py](hitl_context.py)
- [nodes.py](nodes.py)
- [project_workspace/README.md](project_workspace/README.md)
- [../demo8/framework/context.py](../demo8/framework/context.py)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo9/hitl_demo.py
```

## 本节新增能力

- 在 workflow 中插入人工确认节点
- 把 `plan -> approval -> apply` 变成强约束流程
- 在真正写文件前把修改计划展示给人看
- 如果人拒绝修改，终止 workflow 并生成报告
- 复用 `demo8` 的上下文能力，做更安全的代码修改流程

## 关键链路

1. 模型先生成修改计划
2. `ApprovalNode` 把目标文件、修改理由、旧内容、新内容展示出来
3. 只有人明确输入 `yes`，workflow 才会进入真正的写入节点
4. 如果人拒绝，直接进入报告节点

## 学习重点

和 `demo8` 相比，这一节更强调：

- 不是所有任务都应该自动落盘
- 当任务存在风险时，Agent 需要把“执行权”交还给人
- 真正可用的 Agent 系统，很多时候不是更自动，而是更可控

## 示例工作区

- [project_workspace/app.py](project_workspace/app.py)
- [project_workspace/settings.py](project_workspace/settings.py)
- [project_workspace/utils.py](project_workspace/utils.py)
- [project_workspace/README.md](project_workspace/README.md)

## 建议练习

- 给审批节点增加“修改意见后重试”的分支
- 把审批展示信息改得更适合人工审阅
- 思考哪些任务必须经过人确认，哪些任务可以自动执行

## 与上一节相比多了什么

如果 `demo8` 教你的是“如何让流程更稳定”，那么 `demo9` 教你的就是“如何让流程更安全”。

[返回首页](../README.md) | [上一节：demo8](../demo8/README.md) | [下一节：demo10](../demo10/README.md)
