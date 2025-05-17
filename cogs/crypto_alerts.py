# cogs/crypto_alerts.py
import discord
from discord.ext import commands, tasks
import requests
import json
import os
from datetime import datetime
from typing import Optional
from io import BytesIO

CRYPTO_ALERTS_PATH = "data/crypto_alerts.json"

class CryptoAlerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alerts = self.load_alerts()
        self.check_prices.start()

    def load_alerts(self):
        if os.path.exists(CRYPTO_ALERTS_PATH):
            with open(CRYPTO_ALERTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_alerts(self):
        with open(CRYPTO_ALERTS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.alerts, f, indent=2)

    def set_alert(self, user_id: str, symbol: str, target: float, direction: str):
        user_id = str(user_id)
        self.alerts.setdefault(user_id, {})[symbol.upper()] = {
            "target": target,
            "direction": direction
        }
        self.save_alerts()

    def remove_alert(self, user_id: str, symbol: str):
        user_id = str(user_id)
        if user_id in self.alerts and symbol.upper() in self.alerts[user_id]:
            del self.alerts[user_id][symbol.upper()]
            self.save_alerts()

    def get_user_alerts(self, user_id: str):
        return self.alerts.get(str(user_id), {})

    async def fetch_price(self, symbol: str) -> Optional[float]:
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
            resp = requests.get(url)
            data = resp.json()
            return data[symbol.lower()]["usd"]
        except:
            return None

    async def get_chart(self, symbol: str):
        url = f"https://www.tradingview.com/symbols/{symbol.upper()}USD/"
        return url

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip()
        user_id = message.author.id

        args = content.split()
        if not args:
            return

            if args[0].lower() == "清單":
                alerts = self.get_user_alerts(str(user_id))
                if not alerts:
                    await message.channel.send("📭 你沒有設定任何幣別提醒。")
                else:
                    msg = "📋 加密貨幣提醒清單：\n"
                    for s, v in alerts.items():
                        msg += f"- {s} ({'>= ' if v['direction'] == 'up' else '<= '}{v['target']})\n"
                    await message.channel.send(msg)
                return

            if args[0].lower() == "取消" and len(args) == 2:
                self.remove_alert(str(user_id), args[1])
                await message.channel.send(f"❌ 已取消 {args[1]} 的提醒")
                return

            if len(args) == 1:
                symbol = args[0].upper()
                price = await self.fetch_price(symbol)
                if price is None:
                    await message.channel.send(f"⚠️ 無法查詢 {symbol} 價格")
                    return
                url = await self.get_chart(symbol)
                await message.channel.send(f"💰 {symbol} 現價：${price:.2f}\n🔗 {url}")
                return

            if len(args) == 2:
                symbol = args[0].upper()
                try:
                    target = float(args[1])
                except ValueError:
                    await message.channel.send("⚠️ 請輸入正確的數字價格")
                    return

                price = await self.fetch_price(symbol)
                if price is None:
                    await message.channel.send(f"⚠️ 查詢 {symbol} 價格失敗")
                    return

                direction = "up" if price < target else "down"
                self.set_alert(str(user_id), symbol, target, direction)
                await message.channel.send(f"📈 已設定 {symbol} {'突破' if direction == 'up' else '跌破'} ${target} 時通知你")

    @tasks.loop(minutes=3)
    async def check_prices(self):
        for user_id, alert_data in self.alerts.items():
            for symbol, config in alert_data.items():
                price = await self.fetch_price(symbol)
                if price is None:
                    continue
                if config["direction"] == "up" and price >= config["target"]:
                    await self.notify_user(user_id, symbol, price, config)
                    self.remove_alert(user_id, symbol)
                elif config["direction"] == "down" and price <= config["target"]:
                    await self.notify_user(user_id, symbol, price, config)
                    self.remove_alert(user_id, symbol)

    async def notify_user(self, user_id, symbol, price, config):
        user = self.bot.get_user(int(user_id))
        if user:
            url = await self.get_chart(symbol)
            msg = f"📈 幣價提醒：{symbol} 已{'突破' if config['direction'] == 'up' else '跌破'} ${config['target']}，現價：${price:.2f}\n🔗 {url}"
            try:
                await user.send(msg)
            except:
                pass

async def setup(bot):
    await bot.add_cog(CryptoAlerts(bot))
