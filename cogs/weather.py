# cogs/weather.py

import discord
from discord.ext import commands, tasks
from datetime import datetime
from utils import cwb
from discord.abc import Messageable
import traceback

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.noon_weather.start()
        self.evening_weather.start()
        self.tomorrow_weather.start()

    # 取得推播頻道（第一個可用文字頻道）
    async def get_default_channel(self, guild: discord.Guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
        return None

    # 文字查詢指令
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip().lower()

        if content == "天氣":
            await self.send_now_weather(message.channel, include_extra=True)

        elif content.startswith("報時"):
            cmd = content.replace("報時", "").strip()
            if cmd == "now12":
                await self.send_now_weather(message.channel, label="🕛 中午即時天氣", include_extra=True)
            elif cmd == "now18":
                await self.send_now_weather(message.channel, label="🕕 晚上即時天氣", include_extra=False)
            elif cmd == "tomorrow":
                await self.send_tomorrow_weather(message.channel, label="📅 明天天氣預報")
            else:
                await self.send_error(message.channel, "請輸入：報時 now12 / now18 / tomorrow")

    # 即時天氣 + 選擇性加上紫外線/體感
    async def send_now_weather(self, channel: Messageable, label="📡 即時天氣", include_extra=False):
        try:
            weather = await cwb.get_current_weather()
            if "error" in weather:
                return await self.send_error(channel, weather['error'])

            embed = discord.Embed(
                title=label,
                description=f"地點：{weather['地點']}\n🕒 {weather['時間']}",
                color=0x1DA1F2
            )
            embed.add_field(name="🌡️ 溫度", value=weather['溫度'], inline=True)
            embed.add_field(name="💧 濕度", value=weather['濕度'], inline=True)
            embed.add_field(name="☁️ 天氣", value=weather['天氣'], inline=False)

            if include_extra:
                feels = await cwb.get_feels_like()
                uv = await cwb.get_uv_index()
                if "error" not in feels:
                    embed.add_field(name="🌬 體感", value=f"{feels['體感溫度']}（{feels['描述']}）", inline=False)
                if "error" not in uv:
                    embed.add_field(name="🌞 紫外線", value=f"{uv['紫外線指數']}（{uv['等級']}）", inline=False)

            embed.set_footer(text="資料來源：中央氣象署")
            await channel.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await self.send_error(channel, f"即時天氣查詢失敗：{e}")

    # 明天天氣（使用三日預報）
    async def send_tomorrow_weather(self, channel: Messageable, label="📅 明天天氣預報"):
        try:
            data = await cwb.get_tomorrow_forecast()
            if "error" in data:
                return await self.send_error(channel, data['error'])

            embed = discord.Embed(
                title=label,
                description=f"地點：{data['地點']}\n{data['時間範圍']}",
                color=0x00C3A0
            )
            embed.add_field(name="🌤️ 天氣", value=data['天氣'], inline=False)
            embed.add_field(name="🌡️ 氣溫", value=data['溫度'], inline=True)
            embed.add_field(name="☔ 降雨機率", value=data['降雨機率'], inline=True)
            embed.set_footer(text="資料來源：中央氣象署")
            await channel.send(embed=embed)
        except Exception as e:
            traceback.print_exc()
            await self.send_error(channel, f"明天天氣查詢失敗：{e}")

    # 定時任務：每天中午 12:00（含體感/紫外線）
    @tasks.loop(minutes=1)
    async def noon_weather(self):
        now = datetime.now().time()
        if now.hour == 12 and now.minute == 0:
            for guild in self.bot.guilds:
                channel = await self.get_default_channel(guild)
                if channel:
                    await self.send_now_weather(channel, label="🕛 中午天氣報告", include_extra=True)

    # 定時任務：每天晚上 18:00（不含體感/紫外線）
    @tasks.loop(minutes=1)
    async def evening_weather(self):
        now = datetime.now().time()
        if now.hour == 18 and now.minute == 0:
            for guild in self.bot.guilds:
                channel = await self.get_default_channel(guild)
                if channel:
                    await self.send_now_weather(channel, label="🕕 晚上天氣報告", include_extra=False)

    # 定時任務：每天晚上 22:00（明天預報）
    @tasks.loop(minutes=1)
    async def tomorrow_weather(self):
        now = datetime.now().time()
        if now.hour == 22 and now.minute == 0:
            for guild in self.bot.guilds:
                channel = await self.get_default_channel(guild)
                if channel:
                    await self.send_tomorrow_weather(channel)

    # 統一錯誤回報 embed
    async def send_error(self, channel: Messageable, text):
        embed = discord.Embed(
            title="❌ 錯誤",
            description=str(text),
            color=0xFF3333
        )
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Weather(bot))
