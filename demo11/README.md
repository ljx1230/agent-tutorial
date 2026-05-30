[返回首页](../README.md) | [上一节：demo10](../demo10/README.md)

# demo11：MCP Agent Demo

这一节演示的是：在 `demo6` 的最小框架基础上，如何通过 MCP 接入一个标准化外部工具服务。

## 本节目标

- 理解 MCP Server 是怎么把工具暴露给 Agent 的
- 学会通过 `McpServerConfig` 把一个 stdio MCP server 接入 Runtime
- 理解 MCP adapter 在“协议世界”和“本地 ToolRegistry”之间做了什么转换

## 入口文件

- [mcp_agent_demo.py](mcp_agent_demo.py)

## 关键模块

- [mcp_agent_demo.py](mcp_agent_demo.py)
- [weather_server.py](weather_server.py)
- [../demo6/framework/mcp_adapter.py](../demo6/framework/mcp_adapter.py)
- [../demo6/framework/helpers.py](../demo6/framework/helpers.py)

## 运行前准备

确保已经安装根依赖：

```bash
pip install -r requirements.txt
```

并配置：

```powershell
$env:DEEPSEEK_API_KEY="你的 API Key"
```

## 运行方式

```bash
python demo11/mcp_agent_demo.py
```

启动后可以直接试：

- `帮我查一下杭州今天的天气，并给我一个出行建议。`
- `深圳天气怎么样？`
- `支持查哪些城市？`

## 本节新增能力

- 通过 `McpServerConfig` 注册一个通过 stdio 启动的 MCP Server
- 在运行时自动读取 MCP Server 暴露出来的工具列表
- 把 MCP tools 转换成 `demo6` 框架可识别的 `ToolDefinition`
- 让 Agent 在需要天气信息时优先调用 MCP 工具，而不是凭空生成答案

## 这个 demo 里发生了什么

`mcp_agent_demo.py` 会：

1. 创建系统消息，要求遇到天气问题优先调用工具
2. 指定本地 MCP Server 是 [weather_server.py](weather_server.py)
3. 通过 `McpServerConfig(name="weather", command=sys.executable, args=[...])` 注册 server
4. 调用 `create_runtime(...)`，把 MCP tools 一起装进 Runtime
5. 进入多轮对话循环

`weather_server.py` 会：

- 用 `FastMCP("weather-server")` 启动一个本地 MCP Server
- 暴露 `query_weather(city: str)` 工具
- 暴露 `list_supported_cities()` 工具
- 返回内置天气数据，而不是访问外部网络

在接入层里，[../demo6/framework/mcp_adapter.py](../demo6/framework/mcp_adapter.py) 会把这些工具转换成 Runtime 可调用的形式。对这个 demo 来说，最终暴露给 Agent 的工具名会带上 server 前缀，例如：

- `weather_query_weather`
- `weather_list_supported_cities`

## 当前支持的天气数据

本节天气数据来自 [weather_server.py](weather_server.py) 里的本地 `WEATHER_DATA`，当前支持：

- 北京
- 上海
- 杭州
- 深圳

如果用户问了不支持的城市，Agent 应该如实说明当前支持哪些城市，而不是伪造天气数据。

## 学习重点

- MCP Server 负责按协议暴露工具
- Agent Runtime 仍然只认识本地 `ToolDefinition`
- adapter 的职责，是把两边接起来
- 这让你后面可以用统一方式接更多 MCP 生态工具，而不用把所有工具都手写成本地函数

## 建议练习

- 往 `WEATHER_DATA` 里新增一个城市
- 再添加一个新的 MCP 工具，比如“查询穿衣建议”
- 观察如果去掉系统提示里“优先调用天气工具”的约束，模型行为会有什么变化

## 与上一节相比多了什么

`demo10` 解决的是“回答前先查知识库”，`demo11` 解决的是“把标准化外部工具生态接进 Agent”。这一步会让你的 Agent 从“会调用本地工具”进一步走向“会接外部工具协议”。

[返回首页](../README.md) | [上一节：demo10](../demo10/README.md)
