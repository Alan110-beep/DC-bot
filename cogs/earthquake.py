# cogs/earthquake.py
import os
import discord
from discord.ext import commands, tasks
from datetime import datetime
import aiohttp
import traceback

EARTHQUAKE_API = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0015-001"
CWB_TOKEN = os.getenv("CWB_TOKEN")

def build_osm_map_url(lat, lon, zoom=7, width=600, height=300):
    # OpenStreetMap 靜態地圖服務（第三方，無需Google Key）
    return f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={zoom}&size={width},{height}&l=map&pt={lon},{lat},pm2rdm"

class Earthquake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_event_id = None
        self.monitor_earthquakes.start()

    @tasks.loop(seconds=60)
    async def monitor_earthquakes(self):
        try:
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
                        await self.send_earthquake(channel, eq, auto=True)
        except Exception as e:
            print("自動地震推播錯誤：", e)
            traceback.print_exc()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        content = message.content.strip()
        # 「地震」=查詢最近一筆，「地震3」=查詢3筆
        if content.startswith("地震"):
            n = 1
            try:
                n = int(content[2:])
                n = max(1, min(n, 5))
            except:
                pass
            data = await self.fetch_earthquake_data()
            if not data:
                return await message.channel.send("❌ 無法取得地震資料")
            eqs = self.find_multi_events(data, n)
            if not eqs:
                return await message.channel.send("✅ 最近沒有符合條件的地震紀錄")
            for eq in eqs:
                await self.send_earthquake(message.channel, eq)

    async def send_earthquake(self, channel, eq, auto=False):
        embed = discord.Embed(
            title=f"{'【自動推播】' if auto else '【地震速報】'} {eq['location']}",
            color=0xff5555 if eq['magnitude'] >= 5 else 0xffaa33
        )
        embed.add_field(name="時間", value=eq['time'], inline=True)
        embed.add_field(name="規模", value=f"{eq['magnitude']} 級", inline=True)
        embed.add_field(name="深度", value=f"{eq['depth']} 公里", inline=True)
        embed.set_footer(text="資料來源：中央氣象署")
        if eq.get("lat") and eq.get("lon"):
            map_url = build_osm_map_url(eq['lat'], eq['lon'])
            embed.set_image(url=map_url)
        await channel.send(embed=embed)

    def find_valid_event(self, data):
        # 回傳最近一筆台灣本島且規模≥4地震 dict
        try:
            for eq in data["records"]["earthquake"]:
                info = eq["earthquakeInfo"]
                location = info["epiCenter"]["location"]
                magnitude = float(info["magnitude"]["magnitudeValue"])
                if magnitude < 4.0:
                    continue
                if not any(k in location for k in ["臺灣", "台灣", "本島", "花蓮", "台東", "南投", "高雄", "宜蘭", "新竹", "屏東", "台中", "雲林", "彰化", "苗栗", "嘉義"]):
                    continue
                lat = info["epiCenter"].get("latitude")
                lon = info["epiCenter"].get("longitude")
                depth = info["depth"].get("value", "?")
                return {
                    "id": eq["earthquakeNo"],
                    "location": location,
                    "time": info["originTime"],
                    "magnitude": magnitude,
                    "depth": depth,
                    "lat": lat,
                    "lon": lon
                }
        except Exception as e:
            print("地震資料解析錯誤：", e)
            traceback.print_exc()
            return None

    def find_multi_events(self, data, n=1):
        # 回傳多筆地震 [{...}, ...]
        eqs = []
        try:
            for eq in data["records"]["earthquake"]:
                info = eq["earthquakeInfo"]
                location = info["epiCenter"]["location"]
                magnitude = float(info["magnitude"]["magnitudeValue"])
                if magnitude < 4.0:
                    continue
                if not any(k in location for k in ["臺灣", "台灣", "本島", "花蓮", "台東", "南投", "高雄", "宜蘭", "新竹", "屏東", "台中", "雲林", "彰化", "苗栗", "嘉義"]):
                    continue
                lat = info["epiCenter"].get("latitude")
                lon = info["epiCenter"].get("longitude")
                depth = info["depth"].get("value", "?")
                eqs.append({
                    "id": eq["earthquakeNo"],
                    "location": location,
                    "time": info["originTime"],
                    "magnitude": magnitude,
                    "depth": depth,
                    "lat": lat,
                    "lon": lon
                })
                if len(eqs) >= n:
                    break
            return eqs
        except Exception as e:
            print("地震多筆資料解析錯誤：", e)
            traceback.print_exc()
            return []

    async def fetch_earthquake_data(self):
        try:
            async with aiohttp.ClientSession() as session:
                params = {"Authorization": CWB_TOKEN or ""}
                async with session.get(EARTHQUAKE_API, params=params) as resp:
                    return await resp.json()
        except Exception as e:
            print("地震 API 取資料失敗：", e)
            return None

    async def get_default_channel(self, guild: discord.Guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
        return None

async def setup(bot):
    await bot.add_cog(Earthquake(bot))
