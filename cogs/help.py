import discord
from discord.ext import commands
from triggers import TRIGGERS

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        content = message.content.strip().lower()
        if content in ["help", "幫助", "指令", "說明"]:
            # 自動分群
            groups = {}
            for trig, reply_type, group, show_help, help_text in TRIGGERS:
                if show_help:
                    groups.setdefault(group, []).append((trig, help_text))
            embed = discord.Embed(
                title="🤖 Bot 指令說明 & 使用手冊",
                description="本 bot 支援**全中文、純文字自然語言**操作，不用驚嘆號，不用/！\n\n**主要功能一覽：**",
                color=0x3498db
            )
            for group, items in groups.items():
                text = "\n".join([f"【{k}】→ {v}" for k, v in items])
                embed.add_field(name=f"📖 {group}", value=text, inline=False)
            embed.set_footer(text="有新功能會自動更新，歡迎直接體驗！")
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
