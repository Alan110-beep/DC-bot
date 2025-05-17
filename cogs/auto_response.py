# cogs/auto_response.py
import discord
from discord.ext import commands
import random

class AutoResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 十二段御神籤：大吉 > 吉 > 中吉 > 小吉 > 半吉 > 末吉 > 末小吉 > 凶 > 小凶 > 半凶 > 末凶 > 大凶
        self.omikuji_results = [
            ("🌟 大吉", 0xffcc00, "萬事如意，天降好運！"),
            ("✨ 吉", 0xccff66, "吉祥之兆，順勢而行。"),
            ("😊 中吉", 0x99ff99, "努力會有收穫，繼續加油！"),
            ("😌 小吉", 0xccffff, "事情平順，細水長流。"),
            ("🌿 半吉", 0x66ccff, "略有好轉，尚需努力。"),
            ("🍀 末吉", 0x9999ff, "目前平凡，靜待時機。"),
            ("🌱 末小吉", 0x9966ff, "小有好運，惜福惜緣。"),
            ("⚠️ 凶", 0xff6666, "謹言慎行，保持低調。"),
            ("😣 小凶", 0xff3333, "小事易變，保持冷靜。"),
            ("😟 半凶", 0xcc0000, "多有波折，宜防破財。"),
            ("💦 末凶", 0x990000, "風雨將止，尚有轉機。"),
            ("💀 大凶", 0x660000, "諸事不宜，宜靜守不動。")
        ]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip().lower()

        if content == "抽":
            title, color, description = random.choice(self.omikuji_results)
            embed = discord.Embed(
                title=title,
                description=description,
                color=color
            )
            await message.channel.send(embed=embed)
            
async def setup(bot):
    await bot.add_cog(AutoResponse(bot))
