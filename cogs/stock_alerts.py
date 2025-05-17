# cogs/stock_alerts.py
import os
import io
import logging
import discord
from discord.ext import commands, tasks
import yfinance as yf
import ccxt
import aiosqlite
from datetime import datetime
import matplotlib.pyplot as plt
import re

DB_PATH = os.getenv("STOCK_DB", "stock_bot.db")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))

logging.basicConfig(
    filename="stockbot.log",
    filemode="a",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s"
)

def log_error(msg: str):
    logging.error(msg)

def is_stock_symbol(symbol: str) -> bool:
    return symbol.isdigit() and len(symbol) == 4 or symbol.endswith('.TW') or symbol.isalpha()

def normalize_stock_symbol(symbol: str) -> str:
    symbol = symbol.strip().upper()
    if symbol.isdigit() and len(symbol) == 4:
        return symbol + ".TW"
    return symbol

def is_crypto_symbol(symbol: str) -> bool:
    return '/' in symbol

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

def safe_int(val, default=0):
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

def make_price_embed(title, price, open_, high, low, vol, change, symbol) -> discord.Embed:
    color = 0x00ff00 if change >= 0 else 0xff0000
    arrow = "🟢↗" if change >= 0 else "🔴↘"
    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="現價", value=f"`${price:.2f}`", inline=True)
    embed.add_field(name="漲跌", value=f"{arrow} `{change:+.2f}`", inline=True)
    embed.add_field(name="最高/最低", value=f"`{high:.2f}` / `{low:.2f}`", inline=False)
    embed.add_field(name="成交量", value=f"`{vol:,}`", inline=True)
    embed.set_footer(text=f"資料更新時間：{datetime.now():%H:%M:%S}")
    return embed

async def send_error_notify(bot, content: str):
    if ADMIN_USER_ID:
        user = bot.get_user(ADMIN_USER_ID)
        if user:
            await user.send(f"❗股票機器人錯誤通知：\n{content}")

async def plot_kline(symbol: str, days: int = 7):
    df = yf.Ticker(symbol).history(period=f"{days}d")
    if df.empty:
        return None
    fig, ax = plt.subplots()
    df['Close'].plot(ax=ax, lw=2)
    ax.set_title(f"{symbol} 近{days}日收盤價")
    ax.set_ylabel("價格")
    plt.xticks(rotation=45)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf

class StockCN(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.crypto = ccxt.binance()
        self.db_path = DB_PATH
        self.auto_alert.start()

    async def cog_load(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS watchlist (
                user_id INTEGER, symbol TEXT, PRIMARY KEY(user_id, symbol)
            )''')
            await db.execute('''CREATE TABLE IF NOT EXISTS alerts (
                user_id INTEGER, symbol TEXT, target REAL, cond TEXT, PRIMARY KEY(user_id, symbol, target, cond)
            )''')
            await db.commit()

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author.bot or not msg.guild:
            return
        content = msg.content.strip()

        # ==== 查行情 ====
        m = re.match(r"^查\s*([A-Za-z0-9./]+)$", content)
        if m:
            symbol = m.group(1).upper()
            if is_crypto_symbol(symbol):
                await self.query_crypto(msg, symbol)
            else:
                await self.query_stock(msg, symbol)
            return

        # ==== 追蹤 ====
        m = re.match(r"^追蹤\s*([A-Za-z0-9./]+)$", content)
        if m:
            symbol = m.group(1).upper()
            await self.add_watch(msg, symbol)
            return

        # ==== 取消追蹤 ====
        m = re.match(r"^取消追蹤\s*([A-Za-z0-9./]+)$", content)
        if m:
            symbol = m.group(1).upper()
            await self.remove_watch(msg, symbol)
            return

        # ==== 提醒 ====
        m = re.match(r"^提醒\s*([A-Za-z0-9./]+)\s*(大於|小於)\s*([\d.]+)", content)
        if m:
            symbol = m.group(1).upper()
            cond = ">" if m.group(2) == "大於" else "<"
            price = safe_float(m.group(3))
            await self.set_alert(msg, symbol, cond, price)
            return

        # ==== 我的自選 ====
        if content == "我的自選":
            await self.show_watchlist(msg)
            return

        # ==== 我的提醒 ====
        if content == "我的提醒":
            await self.show_alerts(msg)
            return

    # ======= 核心功能區 =======

    async def query_stock(self, msg, symbol):
        symbol = normalize_stock_symbol(symbol)
        try:
            data = yf.Ticker(symbol).history(period='1d')
            if data.empty:
                raise ValueError("查無資料")
            d = data.iloc[-1]
            price = safe_float(d.get('Close'))
            open_ = safe_float(d.get('Open'))
            high = safe_float(d.get('High'))
            low = safe_float(d.get('Low'))
            vol = safe_int(d.get('Volume'))
            change = price - open_
            embed = make_price_embed(f"📈 {symbol} 即時行情", price, open_, high, low, vol, change, symbol)
            kimg = await plot_kline(symbol)
            if kimg:
                file = discord.File(kimg, filename="kline.png")
                embed.set_image(url="attachment://kline.png")
                await msg.reply(embed=embed, file=file)
            else:
                await msg.reply(embed=embed)
        except Exception as e:
            log_error(f"查詢股票失敗: {symbol} | {e}")
            await msg.reply("⚠️ 查無此股票或暫時無法取得資料")
            await send_error_notify(self.bot, f"查股異常: {symbol}\n{e}")

    async def query_crypto(self, msg, symbol):
        try:
            ticker = self.crypto.fetch_ticker(symbol)
            price = safe_float(ticker.get('last'))
            open_ = safe_float(ticker.get('open'))
            change = price - open_
            high = safe_float(ticker.get('high'))
            low = safe_float(ticker.get('low'))
            vol = safe_int(ticker.get('quoteVolume'))
            embed = make_price_embed(f"₿ {symbol} 即時行情", price, open_, high, low, vol, change, symbol)
            await msg.reply(embed=embed)
        except Exception as e:
            log_error(f"查詢幣失敗: {symbol} | {e}")
            await msg.reply("⚠️ 查無此幣種或暫時無法取得資料")
            await send_error_notify(self.bot, f"查幣異常: {symbol}\n{e}")

    async def add_watch(self, msg, symbol):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO watchlist VALUES (?, ?)", (msg.author.id, symbol))
            await db.commit()
        await msg.reply(f"✅ 已加入自選追蹤：{symbol}")

    async def remove_watch(self, msg, symbol):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM watchlist WHERE user_id=? AND symbol=?", (msg.author.id, symbol))
            await db.commit()
        await msg.reply(f"🗑️ 已取消追蹤：{symbol}")

    async def show_watchlist(self, msg):
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("SELECT symbol FROM watchlist WHERE user_id=?", (msg.author.id,))
            symbols = [row[0] for row in await cur.fetchall()]
        if not symbols:
            embed = discord.Embed(
                title="⭐ 你的自選清單",
                description="目前沒有追蹤任何股票/幣種",
                color=0x7289DA
            )
            await msg.reply(embed=embed)
            return
        embed = discord.Embed(
            title=f"⭐ {msg.author.display_name} 的自選清單",
            color=0x00ffcc,
            timestamp=datetime.now()
        )
        stock_list = [normalize_stock_symbol(s) for s in symbols if not is_crypto_symbol(s)]
        crypto_list = [s for s in symbols if is_crypto_symbol(s)]
        for s in stock_list:
            try:
                data = yf.Ticker(s).history(period='1d')
                if data.empty: raise Exception("查無資料")
                d = data.iloc[-1]
                price = safe_float(d.get('Close'))
                open_ = safe_float(d.get('Open'))
                vol = safe_int(d.get('Volume'))
                change = price - open_
                arrow = "🟢" if change >= 0 else "🔴"
                embed.add_field(name=f"{arrow} {s}", value=f"現價 `${price:.2f}`\n成交量 `{vol:,}`", inline=True)
            except Exception:
                embed.add_field(name=f"❓ {s}", value="查詢失敗", inline=True)
        for s in crypto_list:
            try:
                ticker = self.crypto.fetch_ticker(s)
                price = safe_float(ticker.get('last'))
                change = price - safe_float(ticker.get('open'))
                arrow = "🟢" if change >= 0 else "🔴"
                vol = safe_int(ticker.get('quoteVolume'))
                embed.add_field(name=f"{arrow} {s}", value=f"現價 `${price:.2f}`\n成交量 `{vol:,}`", inline=True)
            except Exception:
                embed.add_field(name=f"❓ {s}", value="查詢失敗", inline=True)
        await msg.reply(embed=embed)

    async def set_alert(self, msg, symbol, cond, price):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("INSERT OR IGNORE INTO alerts VALUES (?, ?, ?, ?)", (msg.author.id, symbol, price, cond))
            await db.commit()
        op = "大於" if cond == ">" else "小於"
        await msg.reply(f"🔔 已設定提醒：{symbol} {op} {price}")

    async def show_alerts(self, msg):
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("SELECT symbol, target, cond FROM alerts WHERE user_id=?", (msg.author.id,))
            rows = await cur.fetchall()
        if not rows:
            embed = discord.Embed(
                title="🔔 你的價格提醒",
                description="目前沒有設定任何價格提醒",
                color=0x7289DA
            )
            await msg.reply(embed=embed)
            return
        embed = discord.Embed(
            title=f"🔔 {msg.author.display_name} 的價格提醒",
            color=0xFFD700
        )
        for symbol, price, cond in rows:
            cond_text = "大於" if cond == '>' else "小於"
            embed.add_field(
                name=symbol,
                value=f"▫️ 當價格 {cond_text} `{price:.2f}` 時通知",
                inline=False
            )
        await msg.reply(embed=embed)

    @tasks.loop(minutes=5)
    async def auto_alert(self):
        await self.bot.wait_until_ready()
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("SELECT user_id, symbol, target, cond FROM alerts")
            rows = await cur.fetchall()
        for uid, symbol, target, cond in rows:
            try:
                if is_crypto_symbol(symbol):
                    price = safe_float(self.crypto.fetch_ticker(symbol).get('last'))
                else:
                    s = normalize_stock_symbol(symbol)
                    d = yf.Ticker(s).history(period='1d')
                    price = safe_float(d.iloc[-1].get('Close')) if not d.empty else 0.0
            except Exception as e:
                log_error(f"提醒查詢失敗: {symbol} | {e}")
                continue
            if (cond == ">" and price > target) or (cond == "<" and price < target):
                user = self.bot.get_user(uid)
                if user:
                    try:
                        await user.send(f"🔔 {symbol} 已{'大於' if cond=='>' else '小於'}{target}，現價：`{price:.2f}`")
                    except Exception as e:
                        log_error(f"提醒通知失敗：{user} | {e}")
                async with aiosqlite.connect(self.db_path) as db:
                    await db.execute("DELETE FROM alerts WHERE user_id=? AND symbol=? AND target=? AND cond=?",
                                     (uid, symbol, target, cond))
                    await db.commit()

    async def cog_unload(self):
        self.auto_alert.cancel()

async def setup(bot: commands.Bot):
    await bot.add_cog(StockCN(bot))
