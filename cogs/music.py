# cogs/music.py

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL
from discord import FFmpegPCMAudio, VoiceClient
from typing import Optional, cast, Any, Dict, List

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

class SongInfo:
    def __init__(self, title: str, url: str, webpage_url: str, thumbnail: str, requester: str):
        self.title = title
        self.url = url
        self.webpage_url = webpage_url
        self.thumbnail = thumbnail
        self.requester = requester

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queues: Dict[int, List[SongInfo]] = {}
        self.loop_flags: Dict[int, bool] = {}
        self.now_playing: Dict[int, SongInfo] = {}

    def get_queue(self, guild_id: int) -> List[SongInfo]:
        return self.queues.setdefault(guild_id, [])

    def is_looping(self, guild_id: int) -> bool:
        return self.loop_flags.get(guild_id, False)

    async def send_now_playing(self, message: discord.Message, song: SongInfo):
        embed = discord.Embed(
            title="🎵 正在播放",
            description=f"[{song.title}]({song.webpage_url})",
            color=0x1DB954,
        )
        if song.thumbnail:
            embed.set_thumbnail(url=song.thumbnail)
        embed.add_field(name="點歌者", value=song.requester, inline=True)
        await message.channel.send(embed=embed)

    async def send_queue(self, message: discord.Message, queue: List[SongInfo]):
        embed = discord.Embed(
            title="📜 播放清單",
            color=0x7289DA,
        )
        if not queue:
            embed.description = "播放清單為空"
        else:
            for idx, song in enumerate(queue, 1):
                embed.add_field(
                    name=f"{idx}. {song.title}",
                    value=f"[連結]({song.webpage_url}) | 點歌者: {song.requester}",
                    inline=False,
                )
        await message.channel.send(embed=embed)

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
                song = queue.pop(0)
                self.now_playing[guild.id] = song
                # **這裡已修正參數**
                source = FFmpegPCMAudio(
                    song.url,
                    before_options=FFMPEG_OPTIONS["before_options"],
                    options=FFMPEG_OPTIONS["options"]
                )
                vc.play(source, after=lambda e: self.play_next(message))
                self.bot.loop.create_task(self.send_now_playing(message, song))
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
                    song_infos = []
                    if isinstance(entries, list):
                        for entry in entries:
                            audio_url = entry.get("url")
                            title = entry.get("title", "未知標題")
                            webpage_url = entry.get("webpage_url", query)
                            thumbnail = entry.get("thumbnail", "")
                            if audio_url:
                                song = SongInfo(
                                    title=title,
                                    url=audio_url,
                                    webpage_url=webpage_url,
                                    thumbnail=thumbnail,
                                    requester=message.author.mention,
                                )
                                self.get_queue(guild.id).append(song)
                                song_infos.append(song)
                        if song_infos:
                            await message.channel.send(f"✅ 已加入 {len(song_infos)} 首歌曲到播放清單")
                    else:
                        audio_url = info.get("url")
                        title = info.get("title", "未知標題")
                        webpage_url = info.get("webpage_url", query)
                        thumbnail = info.get("thumbnail", "")
                        if audio_url:
                            song = SongInfo(
                                title=title,
                                url=audio_url,
                                webpage_url=webpage_url,
                                thumbnail=thumbnail,
                                requester=message.author.mention,
                            )
                            self.get_queue(guild.id).append(song)
                            await message.channel.send(f"✅ 已加入播放清單：{title}")

                if vc and isinstance(vc, VoiceClient) and not vc.is_playing():
                    self.play_next(message)

            except Exception as e:
                await message.channel.send(f"❌ 播放錯誤：{e}")

        elif content == "清單":
            queue = self.get_queue(guild.id)
            await self.send_queue(message, queue)

        elif content == "現在播什麼":
            song = self.now_playing.get(guild.id)
            if song:
                await self.send_now_playing(message, song)
            else:
                await message.channel.send("目前沒有正在播放的音樂")

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
