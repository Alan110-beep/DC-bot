# cogs/earthquake.py
import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
import aiohttp
import asyncio
import json
from typing import Dict

EARTHQUAKE_API = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0015-001"
CWB_TOKEN = os.getenv("CWB_TOKEN")

class Earthquake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_event_id = None
        self.monitor_earthquakes.start()

    # 每 60 秒檢查一次新地震
    @tasks.loop(seconds=60)
    async def monitor_earthquakes(self):
        data = await self.fetch_earthquake_data()
        if not data:
            return

        eq = self.find_valid_event(data)
        if not eq:
            return

        if eq["id"] != self.latest_event_id:
            self.latest_event_id = eq["id"]
            for guild in self.bot.guilds:
                channel = await self.get_default_channel(guild)
                if channel:
                    await self.send_earthquake(channel, eq)

    # 指令：地震
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.content.strip().lower() == "地震":
            data = await self.fetch_earthquake_data()
            if not data:
                return await message.channel.send("❌ 無法取得地震資料")

            eq = self.find_valid_event(data)
            if not eq:
                return await message.channel.send("✅ 最近沒有符合條件的地震紀錄")

            await self.send_earthquake(message.channel, eq)

    # 傳送地震訊息（含地圖）
    async def send_earthquake(self, channel, eq):
        msg = (
            f"📍 {eq['location']}\n"
            f"📅 {eq['time']}\n"
            f"⛏️ 規模：{eq['magnitude']}　📏 深度：{eq['depth']} 公里"
        )
        if eq.get("lat") and eq.get("lon"):
            map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={eq['lat']},{eq['lon']}&zoom=7&size=600x300&markers=color:red%7Clabel:E%7C{eq['lat']},{eq['lon']}"
            embed = discord.Embed(description=msg, color=0xff5555)
            embed.set_image(url=map_url)
            await channel.send(embed=embed)
        else:
            await channel.send(msg)

    # 從資料中找出第一筆台灣本島且規模 >= 4 的地震
    def find_valid_event(self, data):
        try:
            for eq in data["records"]["earthquake"]:
                location = eq["earthquakeInfo"]["epiCenter"]["location"]
                magnitude = float(eq["earthquakeInfo"]["magnitude"]["magnitudeValue"])
                if magnitude < 4.0:
                    continue
                if not any(k in location for k in ["臺灣", "台灣", "本島", "花蓮", "台東", "南投", "高雄", "宜蘭", "新竹", "屏東", "台中", "雲林", "彰化", "苗栗", "嘉義"]):
                    continue

                time_str = eq["earthquakeInfo"]["originTime"]
                lat = eq["earthquakeInfo"]["epiCenter"].get("latitude")
                lon = eq["earthquakeInfo"]["epiCenter"].get("longitude")
                depth = eq["earthquakeInfo"]["depth"].get("value", "?")
                return {
                    "id": eq["earthquakeNo"],
                    "location": location,
                    "time": time_str,
                    "magnitude": magnitude,
                    "depth": depth,
                    "lat": lat,
                    "lon": lon
                }
        except Exception:
            return None

    # 取得資料
    async def fetch_earthquake_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                params: Dict[str, str] = {"Authorization": CWB_TOKEN or ""}
                async with session.get(EARTHQUAKE_API, params=params) as resp:
                    return await resp.json()
        except Exception:
            return None

    # 取得預設發送頻道
    async def get_default_channel(self, guild: discord.Guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
        return None

async def setup(bot):
    await bot.add_cog(Earthquake(bot))
