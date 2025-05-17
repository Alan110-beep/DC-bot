# cogs/tasks.py
import discord
from discord.ext import commands
import os
import json
from datetime import datetime, timedelta
import dateparser
import dateparser.search
import plotly.express as px
import pandas as pd
from io import BytesIO

TASKS_PATH = "data/tasks.json"

from discord.ext import tasks

class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = self.load_tasks()
        self.task_reminder_loop.start()

    def load_tasks(self):
        if os.path.exists(TASKS_PATH):
            with open(TASKS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_tasks(self):
        with open(TASKS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, indent=2, ensure_ascii=False)

    def add_task(self, user_id: str, content: str, start: str, end: str):
        user_id = str(user_id)
        self.tasks.setdefault(user_id, []).append({
            "content": content,
            "start": start,
            "end": end,
            "created_at": datetime.utcnow().isoformat(),
            "done": False
        })
        self.save_tasks()

    def update_task_deadline(self, user_id: str, keyword: str, delay_days: int):
        user_id = str(user_id)
        count = 0
        for task in self.tasks.get(user_id, []):
            if keyword in task["content"] and not task["done"]:
                old_end = dateparser.parse(task["end"])
                if old_end:
                    new_end = old_end + timedelta(days=delay_days)
                    task["end"] = new_end.isoformat()
                    count += 1
        self.save_tasks()
        return count

    def delete_task(self, user_id: str, keyword: str):
        user_id = str(user_id)
        before = len(self.tasks.get(user_id, []))
        self.tasks[user_id] = [t for t in self.tasks.get(user_id, []) if keyword not in t["content"]]
        self.save_tasks()
        return before - len(self.tasks[user_id])

    def mark_done(self, user_id: str, keyword: str):
        user_id = str(user_id)
        count = 0
        for task in self.tasks.get(user_id, []):
            if keyword in task["content"] and not task["done"]:
                task["done"] = True
                count += 1
        self.save_tasks()
        return count

    def get_user_tasks(self, user_id: str):
        return self.tasks.get(str(user_id), [])

    def get_recent_done(self, user_id: str):
        user_id = str(user_id)
        now = datetime.utcnow()
        seven_days_ago = now - timedelta(days=7)
        return [t for t in self.tasks.get(user_id, []) if t["done"] and datetime.fromisoformat(t["created_at"]) >= seven_days_ago]

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip()
        user_id = message.author.id

        if content.startswith("任務"):
            await self.handle_add_task(message, user_id, content)
        elif content.startswith("刪任務"):
            keyword = content[4:].strip()
            count = self.delete_task(str(user_id), keyword)
            await message.channel.send(f"🗑️ 已刪除 {count} 筆任務（關鍵字：{keyword}）")
        elif content.startswith("完成"):
            keyword = content[2:].strip()
            count = self.mark_done(str(user_id), keyword)
            await message.channel.send(f"✅ 已標記 {count} 筆任務為完成（關鍵字：{keyword}）")
        elif content.startswith("延後"):
            parts = content.split()
            if len(parts) == 3 and parts[2].endswith("天"):
                keyword = parts[1]
                try:
                    delay = int(parts[2].replace("天", ""))
                    count = self.update_task_deadline(str(user_id), keyword, delay)
                    await message.channel.send(f"⏳ 已延後 {count} 筆任務 {delay} 天")
                except:
                    await message.channel.send("⚠️ 延後格式錯誤，請使用：延後 任務關鍵字 3天")
        elif content == "週計畫":
            await self.send_weekly_timeline(message, user_id)
        elif content == "回顧":
            await self.send_recent_done(message, user_id)
        elif content == "日曆圖":
            await self.send_calendar(message, user_id)

    async def handle_add_task(self, message, user_id, content):
        text = content[2:].strip()
        if "～" in text or "~" in text:
            parts = text.replace("～", "~").split("~")
            if len(parts) == 2:
                left, right = parts
                time_start = dateparser.parse(left.strip(), settings={"PREFER_DATES_FROM": "future"})
                desc_split = right.strip().split(" ", 1)
                if len(desc_split) == 2:
                    time_end = dateparser.parse(desc_split[0], settings={"PREFER_DATES_FROM": "future"})
                    content = desc_split[1].strip()
                    if time_start and time_end and content:
                        self.add_task(user_id, content, time_start.isoformat(), time_end.isoformat())
                        await message.channel.send(f"✅ 已新增任務：{content}（{time_start.date()}～{time_end.date()}）")
                        return
        parsed = dateparser.search.search_dates(text, settings={"PREFER_DATES_FROM": "future"})
        if parsed:
            dt = parsed[-1][1]
            pure_text = text.replace(parsed[-1][0], "").strip()
            self.add_task(user_id, pure_text, dt.isoformat(), dt.isoformat())
            await message.channel.send(f"✅ 已新增任務：{pure_text}（{dt.date()}）")
        else:
            await message.channel.send("⚠️ 請包含有效的時間格式（如：明天、6/10～6/12）")

    async def send_weekly_timeline(self, message, user_id):
        tasks = self.get_user_tasks(user_id)
        now = datetime.utcnow()
        week_end = now + timedelta(days=7)
        data = []
        for t in tasks:
            if not t["done"]:
                start = dateparser.parse(t["start"])
                end = dateparser.parse(t["end"])
                if start and start < week_end:
                    data.append({"任務": t["content"], "開始": start, "結束": end})
        if not data:
            await message.channel.send("📭 本週無排程任務")
            return
        df = pd.DataFrame(data)
        fig = px.timeline(df, x_start="開始", x_end="結束", y="任務", title="🗓️ 本週任務甘特圖")
        fig.update_yaxes(autorange="reversed")
        img_bytes = fig.to_image(format="png")
        buffer = BytesIO(img_bytes)
        await message.channel.send(file=discord.File(buffer, filename="weekly_tasks.png"))

    async def send_recent_done(self, message, user_id):
        done_tasks = self.get_recent_done(user_id)
        if not done_tasks:
            await message.channel.send("📭 最近 7 天內無已完成任務")
            return
        msg = "🕓 最近完成的任務：\n"
        for t in done_tasks:
            msg += f"✅ {t['content']}（完成於 {t['created_at'][:10]}）\n"
        await message.channel.send(msg)

    @tasks.loop(minutes=30)
    async def task_reminder_loop(self):
        now = datetime.utcnow()
        upcoming_window = now + timedelta(hours=2)
        for user_id, user_tasks in self.tasks.items():
            for task in user_tasks:
                if not task.get("done"):
                    end = dateparser.parse(task.get("end", ""))
                    if end and now <= end <= upcoming_window:
                        user = self.bot.get_user(int(user_id)) or await self.bot.fetch_user(int(user_id))
                        if user:
                            try:
                                await user.send(f"⏰ 任務提醒：{task['content']} 預定在 {end.strftime('%m/%d %H:%M')} 到期")
                            except:
                                pass

    async def send_calendar(self, message, user_id):
        tasks = self.get_user_tasks(user_id)
        now = datetime.utcnow()
        start_month = now.replace(day=1)
        end_month = (start_month + timedelta(days=40)).replace(day=1)
        records = []
        for t in tasks:
            if not t["done"]:
                dt = dateparser.parse(t["start"])
                if dt and start_month <= dt < end_month:
                    records.append({"日期": dt.date(), "任務": t["content"]})
        if not records:
            await message.channel.send("📭 本月無任務記錄")
            return
        df = pd.DataFrame(records)
        df["日期"] = pd.to_datetime(df["日期"])
        df_grouped = df.groupby("日期").size().reset_index(name="任務數")
        fig = px.density_heatmap(df_grouped, x="日期", y=["任務數"]*len(df_grouped), z="任務數", nbinsx=31, title="📅 本月任務日曆")
        fig.update_layout(yaxis_showticklabels=False)
        img_bytes = fig.to_image(format="png")
        buffer = BytesIO(img_bytes)
        await message.channel.send(file=discord.File(buffer, filename="monthly_calendar.png"))

async def setup(bot):
    await bot.add_cog(Tasks(bot))
