from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")


WEATHER_DATA = {
    "北京": {
        "weather": "晴",
        "temperature": "28°C",
        "wind": "东北风 2 级",
        "suggestion": "适合外出，但中午注意防晒。",
    },
    "上海": {
        "weather": "多云",
        "temperature": "26°C",
        "wind": "东南风 3 级",
        "suggestion": "体感舒适，适合通勤和散步。",
    },
    "杭州": {
        "weather": "小雨",
        "temperature": "24°C",
        "wind": "西南风 2 级",
        "suggestion": "建议带伞，路面湿滑注意安全。",
    },
    "深圳": {
        "weather": "雷阵雨",
        "temperature": "30°C",
        "wind": "南风 3 级",
        "suggestion": "注意短时强降雨，尽量避开户外长时间停留。",
    },
}


@mcp.tool()
def query_weather(city: str) -> str:
    """
    查询指定城市的天气。
    """
    city = city.strip()
    data = WEATHER_DATA.get(city)

    if data is None:
        available_cities = "、".join(WEATHER_DATA)
        return f"暂时没有 {city} 的天气数据。当前支持的城市：{available_cities}。"

    return (
        f"{city}天气：{data['weather']}，"
        f"气温：{data['temperature']}，"
        f"风力：{data['wind']}。"
        f"建议：{data['suggestion']}"
    )


@mcp.tool()
def list_supported_cities() -> str:
    """列出当前天气 MCP Server 支持查询的城市。"""
    return "当前支持查询的城市：" + "、".join(WEATHER_DATA)


if __name__ == "__main__":
    mcp.run()
