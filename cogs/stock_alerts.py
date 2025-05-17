# cogs/stock_alerts.py
import discord
from discord.ext import commands, tasks
import yfinance as yf
import sqlite3
from typing import Optional
import os
from datetime import datetime
from io import BytesIO

try:
    import plotly.graph_objects as go
except ImportError:
    go = None

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stock_alerts.db")

class StockAlerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.init_db()
        self.check_prices.start()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS alerts (
                        user_id INTEGER,
                        symbol TEXT,
                        direction TEXT,
                        target REAL
                    )''')
        self.conn.commit()

    def set_alert(self, user_id: int, symbol: str, target: float, direction: str):
        self.conn.execute("INSERT INTO alerts (user_id, symbol, direction, target) VALUES (?, ?, ?, ?)",
                          (user_id, symbol.upper(), direction, target))
        self.conn.commit()

    def remove_alert(self, user_id: int, symbol: str):
        self.conn.execute("DELETE FROM alerts WHERE user_id = ? AND symbol = ?", (user_id, symbol.upper()))
        self.conn.commit()

    def get_alerts(self):
        return self.conn.execute("SELECT user_id, symbol, direction, target FROM alerts").fetchall()

    def get_user_alerts(self, user_id):
        return self.conn.execute("SELECT symbol, direction, target FROM alerts WHERE user_id = ?", (user_id,)).fetchall()

    async def fetch_price(self, symbol: str) -> Optional[float]:
        try:
            data = yf.Ticker(symbol).history(period="1d")
            if data is None or data.empty:
                return None
            return data['Close'].iloc[-1]
        except Exception:
            return None

    def is_market_closed(self):
        now = datetime.utcnow().weekday()
        return now >= 5

    def generate_plotly_chart(self, symbol: str):
        if go is None:
            return BytesIO(b"Plotly not available")
        data = yf.download(symbol, period="1mo")
        if data is None or data.empty:
            return BytesIO(b"No data")
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])
        fig.update_layout(title=f"{symbol} K 線圖")
        img_bytes = fig.to_image(format="png")
        return BytesIO(img_bytes)

    async def generate_tradingview_chart(self, symbol: str):
        if async_playwright is None:
            return self.generate_plotly_chart(symbol)
        tv_symbol = f"NASDAQ-{symbol.upper()}" if symbol.isalpha() else f"TWSE-{symbol}"
        url = f"https://www.tradingview.com/symbols/{tv_symbol}/"
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url)
                await page.wait_for_timeout(4000)
                img = await page.screenshot(full_page=True)
                await browser.close()
                return BytesIO(img)
        except:
            return self.generate_plotly_chart(symbol)

    async def get_chart(self, symbol: str):
        if self.is_market_closed():
            return self.generate_plotly_chart(symbol)
        else:
            return await self.generate_tradingview_chart(symbol)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip()
        user_id = message.author.id

        if content.startswith("-"):
            args = content[1:].split()
            if not args:
                return

            if args[0].lower() == "清單":
                alerts = self.get_user_alerts(user_id)
                if not alerts:
                    await message.channel.send("📭 你沒有設定任何股票提醒。")
                else:
                    msg = "📋 目前追蹤清單：\n"
                    for s, d, t in alerts:
                        msg += f"- {s} ({'>= ' if d == 'up' else '<= '}{t})\n"
                    await message.channel.send(msg)
                return

            if args[0].lower() == "取消" and len(args) == 2:
                self.remove_alert(user_id, args[1])
                await message.channel.send(f"❌ 已取消 {args[1]} 的提醒")
                return

            if len(args) == 1:
                symbol = args[0]
                price = await self.fetch_price(symbol)
                if price is None:
                    await message.channel.send(f"⚠️ 無法查詢 {symbol} 的價格")
                    return

                chart = await self.get_chart(symbol)
                embed = discord.Embed(title=f"{symbol.upper()} 即時價格", description=f"💰 現價：${price:.2f}", color=0x00ff00)
                file = discord.File(chart, filename=f"{symbol}.png")
                embed.set_image(url=f"attachment://{symbol}.png")
                await message.channel.send(embed=embed, file=file)
                return

            if len(args) == 2:
                symbol, raw = args
                try:
                    target = float(raw)
                except ValueError:
                    await message.channel.send("⚠️ 請輸入正確的數字價格")
                    return

                price = await self.fetch_price(symbol)
                if price is None:
                    await message.channel.send(f"⚠️ 查詢 {symbol} 價格失敗")
                    return

                direction = "up" if price < target else "down"
                self.set_alert(user_id, symbol, target, direction)
                await message.channel.send(f"📈 已設定 {symbol.upper()} {'突破' if direction=='up' else '跌破'} {target} 時通知你")

    @tasks.loop(minutes=3)
    async def check_prices(self):
        alerts = self.get_alerts()
        for user_id, symbol, direction, target in alerts:
            price = await self.fetch_price(symbol)
            if price is None:
                continue
            if direction == "up" and price >= target:
                await self.notify_user(user_id, symbol, price, target, direction)
                self.remove_alert(user_id, symbol)
            elif direction == "down" and price <= target:
                await self.notify_user(user_id, symbol, price, target, direction)
                self.remove_alert(user_id, symbol)

    async def notify_user(self, user_id, symbol, price, target, direction):
        user = self.bot.get_user(user_id)
        if user:
            msg = f"📈 股票提醒：{symbol.upper()} 已{'突破' if direction=='up' else '跌破'} {target}，現價：${price:.2f}"
            chart = await self.get_chart(symbol)
            file = discord.File(chart, filename=f"{symbol}.png")
            embed = discord.Embed(description=msg, color=0xff9900)
            embed.set_image(url=f"attachment://{symbol}.png")
            try:
                await user.send(embed=embed, file=file)
            except:
                pass

async def setup(bot):
    await bot.add_cog(StockAlerts(bot))
