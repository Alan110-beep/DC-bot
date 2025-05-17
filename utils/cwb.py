# utils/cwb.py
import os
import aiohttp
from typing import Optional, Dict

CWB_TOKEN = os.getenv("CWB_TOKEN")
LOCATION = os.getenv("WEATHER_LOCATION", "新北市")
BASE_URL = "https://opendata.cwb.gov.tw/api/v1/rest/datastore"

async def fetch_cwb(dataset_id: str, extra_params: Optional[Dict[str, Optional[str]]] = None) -> dict:
    url = f"{BASE_URL}/{dataset_id}"

    filtered: Dict[str, str] = {
        "Authorization": CWB_TOKEN or ""
    }
    if extra_params:
        filtered.update({k: v for k, v in extra_params.items() if v is not None})

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=filtered) as resp:
            return await resp.json()

# ✅ 即時天氣
async def get_current_weather() -> dict[str, str]:
    data = await fetch_cwb("O-A0003-001", {"locationName": LOCATION})
    try:
        location = data["records"]["location"][0]
        obs_time = location["time"]["obsTime"]
        temp = location["weatherElement"][3]["elementValue"]
        humidity = location["weatherElement"][4]["elementValue"]
        weather = location["weatherElement"][20]["elementValue"]
        return {
            "地點": LOCATION,
            "時間": obs_time,
            "溫度": f"{temp}°C",
            "濕度": f"{humidity}%",
            "天氣": weather
        }
    except Exception as e:
        return {"error": f"解析失敗：{e}"}

# ✅ 紫外線
async def get_uv_index() -> dict[str, str]:
    data = await fetch_cwb("F-D0047-091", {"locationName": LOCATION})
    try:
        el = data["records"]["locations"][0]["location"][0]["weatherElement"]
        value = el[0]["time"][0]["elementValue"][0]["value"]
        level = el[0]["time"][0]["elementValue"][1]["value"]
        return {
            "紫外線指數": value,
            "等級": level
        }
    except Exception as e:
        return {"error": f"解析 UV 失敗：{e}"}

# ✅ 體感溫度
async def get_feels_like() -> dict[str, str]:
    data = await fetch_cwb("F-D0047-063", {"locationName": LOCATION})
    try:
        el = data["records"]["locations"][0]["location"][0]["weatherElement"]
        value = el[0]["time"][0]["elementValue"][0]["value"]
        desc = el[0]["time"][0]["elementValue"][1]["value"]
        return {
            "體感溫度": f"{value}°C",
            "描述": desc
        }
    except Exception as e:
        return {"error": f"解析體感溫度失敗：{e}"}
    
# ✅ 明天天氣預報
async def get_tomorrow_forecast() -> dict[str, str]:
    data = await fetch_cwb("F-C0032-001", {"locationName": LOCATION})
    try:
        location = data["records"]["location"][0]
        elements = location["weatherElement"]

        weather = elements[0]["time"][1]["parameter"]["parameterName"]
        rain = elements[1]["time"][1]["parameter"]["parameterName"] + "%"
        min_temp = elements[2]["time"][1]["parameter"]["parameterName"]
        max_temp = elements[4]["time"][1]["parameter"]["parameterName"]
        time_range = elements[0]["time"][1]["startTime"][:10]  # YYYY-MM-DD

        return {
            "地點": LOCATION,
            "時間範圍": time_range,
            "天氣": weather,
            "降雨機率": rain,
            "溫度": f"{min_temp}°C ~ {max_temp}°C"
        }
    except Exception as e:
        return {"error": f"解析明天天氣失敗：{e}"}
