# cogs/music.py
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from discord import FFmpegPCMAudio, VoiceClient
from typing import Optional, cast, Any

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True
}

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: dict[int, list[str]] = {}
        self.loop_flags: dict[int, bool] = {}
        self.now_playing: dict[int, str] = {}

    def get_queue(self, guild_id: int) -> list[str]:
        return self.queues.setdefault(guild_id, [])

    def is_looping(self, guild_id: int) -> bool:
        return self.loop_flags.get(guild_id, False)

    def play_next(self, message: discord.Message):
        guild = message.guild
        if not guild:
            return

        vc = guild.voice_client
        queue = self.get_queue(guild.id)

        if vc and isinstance(vc, VoiceClient):
            if self.is_looping(guild.id) and guild.id in self.now_playing:
                queue.insert(0, self.now_playing[guild.id])

            if queue:
                url = queue.pop(0)
                self.now_playing[guild.id] = url
                source = FFmpegPCMAudio(url, executable="ffmpeg")
                vc.play(source, after=lambda e: self.play_next(message))
            else:
                self.now_playing.pop(guild.id, None)
                self.loop_flags[guild.id] = False
                self.queues[guild.id] = []
                if vc.is_connected():
                    self.bot.loop.create_task(vc.disconnect())

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        content = message.content.strip()
        guild = message.guild
        member = cast(discord.Member, message.author)
        vc = guild.voice_client

        if content.startswith("播放"):
            if not member.voice or not member.voice.channel:
                await message.channel.send("❌ 請先加入語音頻道")
                return

            query = content[2:].strip()
            voice_channel = member.voice.channel

            try:
                if not vc or not isinstance(vc, VoiceClient):
                    vc_proto = await voice_channel.connect()
                    vc = cast(VoiceClient, vc_proto)

                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info: Optional[dict[str, Any]] = ydl.extract_info(query, download=False)
                    if not info:
                        await message.channel.send("⚠️ 無法擷取音訊資訊")
                        return

                    entries = info.get("entries") if isinstance(info, dict) else None
                    if isinstance(entries, list):
                        for entry in entries:
                            audio_url = entry.get("url") if isinstance(entry, dict) else None
                            title = entry.get("title", "未知標題") if isinstance(entry, dict) else "未知標題"
                            if audio_url:
                                self.get_queue(guild.id).append(audio_url)
                                await message.channel.send(f"✅ 已加入播放清單：{title}")
                    else:
                        audio_url = info.get("url") if isinstance(info, dict) else None
                        title = info.get("title", "未知標題") if isinstance(info, dict) else "未知標題"
                        if audio_url:
                            self.get_queue(guild.id).append(audio_url)
                            await message.channel.send(f"✅ 已加入播放清單：{title}")

                if vc and isinstance(vc, VoiceClient) and not vc.is_playing():
                    self.play_next(message)

            except Exception as e:
                await message.channel.send(f"❌ 播放錯誤：{e}")

        elif content == "清單":
            queue = self.get_queue(guild.id)
            if not queue:
                await message.channel.send("📭 播放清單為空")
            else:
                msg = "\n".join([f"{i+1}. {url}" for i, url in enumerate(queue)])
                await message.channel.send(f"📜 當前清單：\n{msg}")

        elif content == "跳過":
            if vc and isinstance(vc, VoiceClient) and vc.is_playing():
                vc.stop()
                await message.channel.send("⏭ 已跳過")
            else:
                await message.channel.send("⚠️ 沒有正在播放的音樂")

        elif content == "停止":
            if vc and isinstance(vc, VoiceClient):
                self.get_queue(guild.id).clear()
                self.loop_flags[guild.id] = False
                await vc.disconnect(force=True)
                await message.channel.send("🛑 已停止播放並離開語音頻道")
            else:
                await message.channel.send("⚠️ 機器人未連接語音頻道")

        elif content == "重播":
            self.loop_flags[guild.id] = not self.loop_flags.get(guild.id, False)
            await message.channel.send(f"🔁 循環模式：{'✅ 開啟' if self.loop_flags[guild.id] else '❌ 關閉'}")

        elif content == "暫停":
            if vc and isinstance(vc, VoiceClient) and vc.is_playing():
                vc.pause()
                await message.channel.send("⏸ 已暫停播放")
            else:
                await message.channel.send("⚠️ 沒有正在播放的音樂")

        elif content == "繼續":
            if vc and isinstance(vc, VoiceClient) and vc.is_paused():
                vc.resume()
                await message.channel.send("▶️ 已繼續播放")
            else:
                await message.channel.send("⚠️ 沒有音樂可以繼續")

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
