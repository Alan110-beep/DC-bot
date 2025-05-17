import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import traceback

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("❌ 未提供 DISCORD_TOKEN，請確認 .env 是否正確")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True

COGS_DIR = "cogs"

class StarBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 自動讀取 cogs 目錄下所有 .py 檔案
        cogs = [
            f"{COGS_DIR}.{f[:-3]}"
            for f in os.listdir(COGS_DIR)
            if f.endswith(".py") and not f.startswith("_")
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ 成功載入 {cog}")
            except Exception as e:
                print(f"❌ 載入 {cog} 失敗：{e}")
                traceback.print_exc()

bot = StarBot()

@bot.event
async def on_ready():
    if bot.user:
        print(f"✅ 已登入為：{bot.user}（ID: {bot.user.id}）")

bot.run(TOKEN)
