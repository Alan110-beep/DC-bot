# cogs/music.py
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio, VoiceClient
from typing import Optional, cast

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True
}

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: dict[int, list[str]] = {}

    def get_queue(self, guild_id: int) -> list[str]:
        return self.queues.setdefault(guild_id, [])

    def play_next(self, message: discord.Message):
        guild = message.guild
        if not guild:
            return

        vc = guild.voice_client
        queue = self.get_queue(guild.id)

        if vc and isinstance(vc, VoiceClient) and queue:
            url = queue.pop(0)
            source = FFmpegPCMAudio(url, executable="ffmpeg")
            vc.play(source, after=lambda e: self.play_next(message))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip()
        guild = message.guild
        member = cast(discord.Member, message.author)

        # play 指令
        if content.lower().startswith("play "):
            if not member.voice or not member.voice.channel:
                await message.channel.send("❌ 請先加入語音頻道")
                return

            url = content[5:].strip()
            voice_channel = member.voice.channel
            vc = guild.voice_client

            try:
                if not vc or not isinstance(vc, VoiceClient):
                    vc_proto = await voice_channel.connect()
                    vc = cast(VoiceClient, vc_proto)

                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    if not info:
                        await message.channel.send("⚠️ 無法讀取音訊資訊")
                        return

                    audio_url = info.get("url")
                    title = info.get("title", "未知標題")

                    if not audio_url:
                        await message.channel.send("⚠️ 影片無音訊資料")
                        return

                    self.get_queue(guild.id).append(audio_url)

                if not vc.is_playing():
                    self.play_next(message)

                await message.channel.send(f"▶️ 播放中：{title}")
            except Exception as e:
                await message.channel.send(f"❌ 播放錯誤：{e}")

        # skip 指令
        elif content.lower() == "skip":
            vc = guild.voice_client
            if isinstance(vc, VoiceClient) and vc.is_playing():
                vc.stop()
                await message.channel.send("⏭ 已跳過")
            else:
                await message.channel.send("⚠️ 沒有正在播放的音樂")

        # stop 指令
        elif content.lower() == "stop":
            vc = guild.voice_client
            if isinstance(vc, VoiceClient):
                self.get_queue(guild.id).clear()
                await vc.disconnect(force=True)
                await message.channel.send("🛑 已停止播放並離開語音頻道")
            else:
                await message.channel.send("⚠️ 機器人未連接語音頻道")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
