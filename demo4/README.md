[返回首页](../README.md) | [上一节：demo3](../demo3/README.md) | [下一节：demo5](../demo5/README.md)

# demo4：Planning Demo

这一节把“先做什么、后做什么”显式化，让模型不再直接冲着结果输出，而是先决定下一步动作。

## 本节目标

- 理解 Planning 为什么适合做结构化任务推进
- 学会把任务拆成多个步骤和动作
- 理解“模型负责决策，程序负责执行”的边界

## 入口文件

- [planning_demo.py](planning_demo.py)

## 运行方式

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

```bash
python demo4/planning_demo.py
```

## 本节新增能力

- 把任务拆成多个步骤
- 维护结构化状态 `state`
- 让模型只返回 JSON 决策
- 通过动作枚举控制执行流程
- 在 `decide_path -> draft_content -> create_file -> finish` 之间推进任务

## 学习重点

- `create_system_message()`：如何严格约束输出格式和动作集合
- `build_state_message()`：如何把当前状态整理给模型
- `call_planner()`：如何把“规划器”当作一个只做决策的模型调用
- `run_task_agent()`：如何在程序侧接管执行流程

这一节最值得体会的，是“模型负责决策，程序负责执行”的边界感。

## 建议练习

- 新增一个动作，比如“先总结需求”
- 改动状态结构，观察流程稳定性会不会变化
- 对比“先规划后执行”和“直接生成最终结果”的体验差异

## 与上一节相比多了什么

`demo3` 已经能调用工具，但模型自由度还比较高。`demo4` 开始把任务推进做成显式状态机，模型更可控，任务执行也更稳定。

[返回首页](../README.md) | [上一节：demo3](../demo3/README.md) | [下一节：demo5](../demo5/README.md)
