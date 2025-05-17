# bot.py
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ 未提供 DISCORD_TOKEN，請確認 .env 是否正確")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

class StarBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        cogs = [
            "cogs.music",
            "cogs.auto_response",
            "cogs.weather",
            "cogs.weather_alerts",
            "cogs.earthquake",
            "cogs.stock_alerts",
            "cogs.task",
            "cogs.crypto_alerts"
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ 成功載入 {cog}")
            except Exception as e:
                print(f"❌ 載入 {cog} 失敗：{e}")

bot = StarBot()

@bot.event
async def on_ready():
    if bot.user:
        print(f"✅ 已登入為：{bot.user}（ID: {bot.user.id}）")

bot.run(TOKEN)
