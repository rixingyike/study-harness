#!/usr/bin/env python3
"""
Study-Harness 方案一: 基于标准 MCP 协议的天气查询与对比扩展服务
数据源: wttr.in 免费天气开放接口 (零 API Key，开箱即用)
"""
import sys
import json
import urllib.parse
import urllib.request

# 兼容 FastMCP 与 MCPServer
try:
    from mcp.server.fastmcp import FastMCP
    app = FastMCP("weather-service")
except ImportError:
    try:
        from mcp.server.mcpserver import MCPServer
        app = MCPServer("weather-service")
    except Exception as e:
        print(f"Error importing MCP server: {e}", file=sys.stderr)
        sys.exit(1)

# 常见国内城市中英文与别名映射，确保中英文输入均能稳定解析
CITY_MAP = {
    "北京": "Beijing",
    "上海": "Shanghai",
    "广州": "Guangzhou",
    "深圳": "Shenzhen",
    "杭州": "Hangzhou",
    "成都": "Chengdu",
    "武汉": "Wuhan",
    "南京": "Nanjing",
    "西安": "Xian",
    "重庆": "Chongqing",
    "天津": "Tianjin",
    "苏州": "Suzhou",
    "香港": "HongKong",
    "台北": "Taipei"
}

WEATHER_DESC_CN = {
    "Sunny": "晴朗",
    "Clear": "晴朗",
    "Partly cloudy": "多云",
    "Partly Cloudy": "多云",
    "Cloudy": "阴天",
    "Overcast": "阴天",
    "Mist": "薄雾",
    "Fog": "浓雾",
    "Light rain": "小雨",
    "Moderate rain": "中雨",
    "Heavy rain": "大雨",
    "Patchy rain possible": "局部可能有小雨",
    "Thundery outbreaks possible": "可能有雷阵雨",
    "Light snow": "小雪",
    "Moderate snow": "中雪",
    "Heavy snow": "大雪"
}

def fetch_wttr_data(city: str) -> dict:
    """向 wttr.in 发起 HTTP 请求获取 JSON 天气数据"""
    query_city = CITY_MAP.get(city.strip(), city.strip())
    encoded_city = urllib.parse.quote(query_city)
    url = f"http://wttr.in/{encoded_city}?format=j1"
    headers = {"User-Agent": "curl/7.81.0"}

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def parse_day_weather(data: dict, day: str = "tomorrow") -> dict:
    """解析指定日期（今天/明天）的天气数据"""
    weather_list = data.get("weather", [])
    if not weather_list:
        raise ValueError("wttr.in 返回数据中未包含预报信息")

    # 0 代表今天，1 代表明天，2 代表后天
    idx = 1 if (day in ["tomorrow", "明天", "1"]) else 0
    if len(weather_list) <= idx:
        idx = 0

    target = weather_list[idx]
    hourly = target.get("hourly", [])
    mid_hourly = hourly[len(hourly) // 2] if hourly else {}
    raw_desc = mid_hourly.get("weatherDesc", [{}])[0].get("value", "Unknown")
    desc_cn = WEATHER_DESC_CN.get(raw_desc, raw_desc)

    return {
        "date": target.get("date"),
        "max_temp_c": int(target.get("maxtempC", 0)),
        "min_temp_c": int(target.get("mintempC", 0)),
        "avg_temp_c": int(target.get("avgtempC", 0)),
        "condition": f"{raw_desc} ({desc_cn})"
    }

@app.tool()
def get_weather(city: str, day: str = "tomorrow") -> str:
    """
    查询指定城市的天气预报（支持今天或明天）。
    参数:
      city: 城市名称（如 '北京'、'上海'、'Beijing' 等）
      day: 预报日期，可选 'today'（今天）或 'tomorrow'（明天），默认 'tomorrow'
    """
    try:
        data = fetch_wttr_data(city)
        w = parse_day_weather(data, day=day)
        day_label = "明天" if (day in ["tomorrow", "明天", "1"]) else "今天"

        return (
            f"【城市天气预报】\n"
            f"城市: {city}\n"
            f"日期: {w['date']} ({day_label})\n"
            f"最高温度: {w['max_temp_c']}°C\n"
            f"最低温度: {w['min_temp_c']}°C\n"
            f"平均温度: {w['avg_temp_c']}°C\n"
            f"天气状况: {w['condition']}"
        )
    except Exception as e:
        return f"查询城市 [{city}] 天气失败: {str(e)}"

@app.tool()
def compare_weather(city1: str, city2: str, day: str = "tomorrow") -> str:
    """
    对比两个城市在指定日期（如明天）的温度高低及温差。
    参数:
      city1: 第一个城市名称（如 '北京'）
      city2: 第二个城市名称（如 '上海'）
      day: 预报日期，默认 'tomorrow'（明天）
    """
    try:
        data1 = fetch_wttr_data(city1)
        w1 = parse_day_weather(data1, day=day)

        data2 = fetch_wttr_data(city2)
        w2 = parse_day_weather(data2, day=day)

        day_label = "明天" if (day in ["tomorrow", "明天", "1"]) else "今天"
        diff_max = abs(w1["max_temp_c"] - w2["max_temp_c"])
        diff_avg = abs(w1["avg_temp_c"] - w2["avg_temp_c"])

        if w1["max_temp_c"] > w2["max_temp_c"]:
            higher_city = city1
            lower_city = city2
        elif w1["max_temp_c"] < w2["max_temp_c"]:
            higher_city = city2
            lower_city = city1
        else:
            higher_city = "两地最高温相同"
            lower_city = ""

        return (
            f"【{day_label}气温对比报告 ({city1} vs {city2})】\n"
            f"日期: {w1['date']}\n"
            f"1. {city1}: 最高 {w1['max_temp_c']}°C，最低 {w1['min_temp_c']}°C，平均 {w1['avg_temp_c']}°C，状况: {w1['condition']}\n"
            f"2. {city2}: 最高 {w2['max_temp_c']}°C，最低 {w2['min_temp_c']}°C，平均 {w2['avg_temp_c']}°C，状况: {w2['condition']}\n"
            f"结论: {day_label}{higher_city}的气温更高。以最高温度对比，{higher_city}比{lower_city}高出 {diff_max}°C；以平均温度对比，相差 {diff_avg}°C。"
        )
    except Exception as e:
        return f"对比 [{city1}] 与 [{city2}] 天气失败: {str(e)}"

if __name__ == "__main__":
    app.run(transport="stdio")
