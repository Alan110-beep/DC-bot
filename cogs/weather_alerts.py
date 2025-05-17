# cogs/weather_alerts.py
import os
import discord
from discord.ext import commands, tasks
import aiohttp
from typing import Dict
from datetime import datetime

CWB_TOKEN = os.getenv("CWB_TOKEN")
WEATHER_ALERT_API = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/W-C0033-001"
OBSERVATION_API = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/O-A0003-001"
WIND_ALERT_API = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/W-C0033-002"
UV_API = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-D0047-091"
LOCATION = os.getenv("WEATHER_LOCATION", "新北市")

class WeatherAlerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_alerts: set[str] = set()
        self.last_humidity_alert = None
        self.last_uv_alert = None
        self.monitor_weather_alerts.start()

    @tasks.loop(minutes=10)
    async def monitor_weather_alerts(self):
        try:
            await self.check_heavy_rain()
            await self.check_strong_wind()
            await self.check_high_humidity()
            await self.check_high_uv()
        except Exception as e:
            print("氣象自動推播錯誤：", e)

    async def check_heavy_rain(self):
        alert_data = await self.fetch_dataset(WEATHER_ALERT_API)
        if alert_data:
            for alert in alert_data.get("records", {}).get("location", []):
                if LOCATION in alert.get("locationName", ""):
                    for item in alert.get("hazardConditions", {}).get("hazards", []):
                        phenomenon = item.get("phenomena")
                        if phenomenon and ("豪雨" in phenomenon):
                            alert_id = f"{alert['locationName']}_{phenomenon}"
                            if alert_id not in self.last_alerts:
                                self.last_alerts.add(alert_id)
                                await self.broadcast_embed(
                                    title=f"⚠️ {LOCATION} 豪雨特報",
                                    desc=f"{LOCATION} 發布 {phenomenon} 特報！\n請注意行車安全、防範淹水。", color=0x0055ff
                                )

    async def check_strong_wind(self):
        wind_data = await self.fetch_dataset(WIND_ALERT_API)
        if wind_data:
            for alert in wind_data.get("records", {}).get("location", []):
                if LOCATION in alert.get("locationName", ""):
                    for item in alert.get("hazardConditions", {}).get("hazards", []):
                        phenomenon = item.get("phenomena")
                        if phenomenon and ("強風" in phenomenon or "陣風" in phenomenon):
                            alert_id = f"{alert['locationName']}_{phenomenon}"
                            if alert_id not in self.last_alerts:
                                self.last_alerts.add(alert_id)
                                await self.broadcast_embed(
                                    title=f"💨 {LOCATION} 強風特報",
                                    desc=f"{LOCATION} 發布 {phenomenon} 特報！\n請注意高空物品、行走安全。", color=0x00bbcc
                                )

    async def check_high_humidity(self):
        obs_data = await self.fetch_dataset(OBSERVATION_API, {"locationName": LOCATION})
        if obs_data:
            try:
                location = obs_data["records"]["location"][0]
                humidity = int(location["weatherElement"][4]["elementValue"])
                if humidity >= 90:
                    today = datetime.now().date()
                    if self.last_humidity_alert != today:
                        self.last_humidity_alert = today
                        await self.broadcast_embed(
                            title=f"💧 {LOCATION} 濕度警報",
                            desc=f"{LOCATION} 濕度過高：{humidity}%\n建議通風防潮，注意電子設備保養。",
                            color=0x33bbff
                        )
            except Exception as e:
                print("濕度資料處理失敗：", e)

    async def check_high_uv(self):
        uv_data = await self.fetch_dataset(UV_API, {"locationName": LOCATION})
        if uv_data:
            try:
                el = uv_data["records"]["locations"][0]["location"][0]["weatherElement"]
                uv_index = float(el[0]["time"][0]["elementValue"][0]["value"])
                uv_level = el[0]["time"][0]["elementValue"][1]["value"]
                today = datetime.now().date()
                if uv_index >= 8 and self.last_uv_alert != today:
                    self.last_uv_alert = today
                    await self.broadcast_embed(
                        title=f"🟣 紫外線警報 {uv_index}（{uv_level}）",
                        desc="紫外線指數過高，請加強防曬，避免長時間戶外活動。",
                        color=0xaa55ff
                    )
            except Exception as e:
                print("UV資料處理失敗：", e)

    async def fetch_dataset(self, url: str, params: Dict[str, str] | None = None):
        try:
            if params is None:
                params = {}
            params["Authorization"] = CWB_TOKEN or ""
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    return await resp.json()
        except Exception as e:
            print("氣象API取資料失敗：", e)
            return None

    async def broadcast_embed(self, title, desc, color):
        embed = discord.Embed(title=title, description=desc, color=color)
        embed.set_footer(text="資料來源：中央氣象署")
        for guild in self.bot.guilds:
            channel = await self.get_default_channel(guild)
            if channel:
                await channel.send(embed=embed)

    async def get_default_channel(self, guild: discord.Guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
        return None

async def setup(bot):
    await bot.add_cog(WeatherAlerts(bot))
