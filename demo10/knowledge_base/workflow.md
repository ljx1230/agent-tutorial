# Workflow

Workflow 关注的是稳定、可控、可解释的流程编排。

和 ReAct 自由循环不同，Workflow 会提前定义好阶段，例如：

- classify：判断任务类型。
- inspect：读取上下文。
- plan：生成计划。
- apply：执行修改。
- verify：验证结果。
- report：总结输出。

Workflow 更适合流程边界清晰、步骤可预期的任务。ReAct 更适合开放问题和需要模型自主探索的任务。

在真实项目中，二者经常组合使用：Workflow 负责外层流程，ReAct 可以作为某个节点内部的决策策略。
