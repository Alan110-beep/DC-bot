import discord
from discord.ext import commands
import random

class AutoResponse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 御神籤
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
        # 多則笑話
        self.jokes = [
            "你知道為什麼電腦不會感冒嗎？因為有防毒軟體！",
            "有一天 CPU 去爬山，結果過熱了。",
            "小明問：『你會寫程式嗎？』我答：『不會啊，只會 debug。』",
            "老師：『請用 Python 寫一首詩。』\n學生：『import this』",
            "為什麼機器人都很有禮貌？因為他們都有 protocol。",
            "工程師的減肥方法：刪掉 cookies。",
            "為什麼 AI 不會失戀？因為參數早就調好了。"
        ]
        # 安慰語
        self.comforts = [
            "別灰心，你很棒的！",
            "休息一下，等下會更好喔！",
            "沒關係，一切都會過去的。",
            "抱抱，不要難過！",
            "人生嘛，就是起起伏伏，慢慢來。"
        ]
        # 嗆語
        self.taunts = [
            "哎呀，這麼菜還敢出來玩？",
            "你認真了嗎？我都還沒使出全力呢！",
            "哈哈，這操作不及格唷！",
            "再努力一點，或許下次能贏我！"
        ]
        # 常用情緒互動
        self.greetings = {
            "早安": "早安安 ☀️",
            "午安": "午安安 🌞",
            "晚安": "晚安，祝你好夢！"
        }
        # 彩蛋
        self.easter_eggs = {
            "我想中樂透": "中頭獎的機率是……你還是努力點比較快！",
            "你會說台語嗎": "我咧學啦～逐家好，我是 Discord 機器人。"
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content = message.content.strip().lower()

        # 1. 御神籤
        if content == "抽":
            title, color, description = random.choice(self.omikuji_results)
            embed = discord.Embed(
                title=title,
                description=f"{message.author.mention}\n{description}",
                color=color
            )
            await message.channel.send(embed=embed)
            return

        # 2. 笑話
        if content == "笑話":
            joke = random.choice(self.jokes)
            embed = discord.Embed(
                title="🤖 小機器人冷笑話",
                description=joke,
                color=0x6C3483
            )
            await message.channel.send(embed=embed)
            return

        # 3. 互動回覆
        if content in self.greetings:
            embed = discord.Embed(
                title="👋 問候時間",
                description=f"{message.author.mention} {self.greetings[content]}",
                color=0x5DADE2
            )
            await message.channel.send(embed=embed)
            return

        if content == "吃飯了嗎":
            embed = discord.Embed(
                title="🍚 溫馨提醒",
                description=f"{message.author.mention} 我不會餓，但你要記得吃飯喔！",
                color=0x27AE60
            )
            await message.channel.send(embed=embed)
            return

        if "貼貼" in content:
            embed = discord.Embed(
                title="🤗 貼貼",
                description=f"{message.author.mention} 給大家貼貼！",
                color=0xFFB6C1
            )
            await message.channel.send(embed=embed)
            return

        if "抱抱" in content:
            embed = discord.Embed(
                title="🧸 抱抱",
                description=f"{message.author.mention} （暖暖地抱緊你）",
                color=0xD7BDE2
            )
            await message.channel.send(embed=embed)
            return

        if content == "安慰我":
            reply = random.choice(self.comforts)
            embed = discord.Embed(
                title="💖 安慰服務",
                description=f"{message.author.mention} {reply}",
                color=0xF1948A
            )
            await message.channel.send(embed=embed)
            return

        if content == "嗆我":
            reply = random.choice(self.taunts)
            embed = discord.Embed(
                title="😏 嗆爆服務",
                description=f"{message.author.mention} {reply}",
                color=0x566573
            )
            await message.channel.send(embed=embed)
            return

        # 4. 彩蛋
        for key, reply in self.easter_eggs.items():
            if key in content:
                embed = discord.Embed(
                    title="🥚 彩蛋發現",
                    description=f"{message.author.mention} {reply}",
                    color=0xF7CA18
                )
                await message.channel.send(embed=embed)
                return

async def setup(bot):
    await bot.add_cog(AutoResponse(bot))
