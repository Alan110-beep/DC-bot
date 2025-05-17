# cogs/weather.py
import discord
from discord.ext import commands, tasks
from datetime import datetime
from utils import cwb
from discord.abc import Messageable

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
                await message.channel.send("請輸入：報時 now12 / now18 / tomorrow")

    # 即時天氣 + 選擇性加上紫外線/體感
    async def send_now_weather(self, channel: Messageable, label="📡 即時天氣", include_extra=False):
        weather = await cwb.get_current_weather()
        if "error" in weather:
            await channel.send(f"❌ {weather['error']}")
            return

        msg = (
            f"{label}（{weather['地點']}）\n"
            f"🕒 {weather['時間']}\n"
            f"🌡️ {weather['溫度']}　💧 {weather['濕度']}\n"
            f"☁️ 天氣：{weather['天氣']}"
        )

        if include_extra:
            feels = await cwb.get_feels_like()
            uv = await cwb.get_uv_index()
            if "error" not in feels:
                msg += f"\n🌬 體感：{feels['體感溫度']}（{feels['描述']}）"
            if "error" not in uv:
                msg += f"\n🌞 紫外線：{uv['紫外線指數']} 等級：{uv['等級']}"

        await channel.send(msg)

    # 明天天氣（使用三日預報）
    async def send_tomorrow_weather(self, channel: Messageable, label="📅 明天天氣預報"):
        data = await cwb.get_tomorrow_forecast()
        if "error" in data:
            await channel.send(f"❌ {data['error']}")
            return

        msg = (
            f"{label}（{data['地點']}）\n"
            f"📅 {data['時間範圍']}\n"
            f"🌤️ 天氣：{data['天氣']}\n"
            f"🌡️ 氣溫：{data['溫度']}\n"
            f"☔ 降雨：{data['降雨機率']}"
        )
        await channel.send(msg)

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

async def setup(bot):
    await bot.add_cog(Weather(bot))
