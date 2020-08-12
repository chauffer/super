import os
import tempfile
import asyncio
import math
from collections import defaultdict
from contextlib import suppress
from time import time
import youtube_dl
import discord
from super.settings import SUPER_HELP_COLOR, SUPER_QUEUE_PAGINATION as S_Q_P
from ago import human


class Server:
    def __init__(self, bot, serverid):
        self.bot = bot
        self.id = serverid
        self.channel = None
        self._queue = []
        self.playing = None

    def __str__(self):
        return self.id

    @property
    def voice_client(self):
        return get_voice_client(self.bot, self.id)

    def song_ended(self, error):
        with suppress(Exception):
            self.playing.remove()
        if self._queue:
            with suppress(Exception):  # run play_next async
                asyncio.run_coroutine_threadsafe(self.play_next, self.bot.loop).result()

    async def queue(self, song):
        song.get_metadata()
        self._queue.append(song)
        if not self.is_playing:
            return await self.play_next()
        return await song.display_queued(len(self._queue))

    async def current_song(self, ctx):
        embed = discord.Embed(type="rich", color=SUPER_HELP_COLOR)
        embed.set_author(name="now playing")
        embed.add_field(
            name=self.playing.metadata["title"],
            value=f"by {self.playing.user}",
            inline=False,
        )
        return await ctx.message.channel.send(embed=embed)

    @property
    def is_playing(self):
        if not self.voice_client:
            return None

        return self.voice_client.is_playing()

    @property
    def is_paused(self):
        return self.voice_client.is_paused()

    @property
    def is_connected(self):
        if not self.voice_client:
            return False

        return self.voice_client.is_connected()

    @property
    def _queuepages(self):
        return math.ceil(len(self._queue) / S_Q_P)

    def _queuep(self, page):
        '''returns paginated queue'''
        return self._queue[(page - 1) * S_Q_P : page * S_Q_P]

    async def connect(self):
        if self.channel and not self.is_connected:
            return await self.channel.connect(timeout=3, reconnect=True)

    async def disconnect(self):
        return await self.voice_client.disconnect()

    async def resume(self):
        return await self.voice_client.resume()

    async def pause(self):
        return await self.voice_client.pause()

    async def play_next(self):
        if not self._queue:
            return

        if self.playing:
            self.playing.remove()

        self.playing = self._queue.pop(0)
        await self.connect()
        await self.playing.play()

    async def display_queue(self, ctx, page):
        if not self._queue:
            return await ctx.message.channel.send("nothing's queued")

        embed = discord.Embed(type="rich", color=SUPER_HELP_COLOR)
        embed.set_author(name="Song Queue")

        [embed.add_field(name=f"**{index}.** {song.title_duration}", inline=False)
        for index, song in enumerate(self._queuep(page), start=1)]

        embed.set_footer(
            text=f"page {page} of {self._queuepages)}"
        )

        return await ctx.message.channel.send(embed=embed)


class Song:
    """Song object"""

    def __init__(self, url, server, message):
        self.url = url
        self.server = server
        self.channel = message.channel
        self.user = message.author
        self.metadata = None
        self.path = (
            os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))
            + ".mp3"
        )
        self.is_downloaded = False
        self.added_at = time()

    def __str__(self):
        return f"**{self.url}** added {self.ago} by {self.user}"

    @property
    def ago(self):
        return human(self.added_at, precision=2)

    @property
    def is_playing(self):
        return self.server.is_playing and self.server.playing == self

    @property
    def title_duration(self):
        m, s = self.metadata["duration"] / 60, self.metadata["duration"] % 60
        return f"{self.metadata['title']} [{m}:{s}]"

    def remove(self):
        self.is_downloaded = False
        with suppress(Exception):
            os.remove(self.path)

    def get_metadata(self):
        """ Fetch song metadata using youtube_dl """
        with youtube_dl.YoutubeDL() as ydl:
            self.metadata = ydl.extract_info(self.url, download=False)

    def download(self):
        """ Download song using youtube_dl """

        ydl_options = {
            "outtmpl": self.path,
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "verbose": True,
        }
        print(ydl_options)
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            print("Downloaded to", self.path)
            ydl.download([self.url])
            self.is_downloaded = True

    async def now_playing(self):
        embed = discord.Embed(
            title=self.title_duration,
            url=self.url,
            description=f'uploader: {self.metadata["uploader"]}',
            color=SUPER_HELP_COLOR,
            type="rich",
        )
        embed.set_author(name=f"now playing, by {self.user.mention}")
        embed.set_thumbnail(url=self.metadata["thumbnail"])
        await self.channel.send(embed=embed)

    async def display_queued(self, index):
        embed = discord.Embed(
            title=self.metadata["title"],
            url=self.url,
            color=SUPER_HELP_COLOR,
            type="rich",
        )
        embed.set_author(name=f"queued in position #{index}...")
        embed.set_thumbnail(url=self.metadata["thumbnail"])
        await self.channel.send(embed=embed)

    async def play(self):
        if not self.is_downloaded:
            self.download()
        print("Playing", self.path)
        await self.now_playing()
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.path))
        self.server.voice_client.play(source, after=self.server.song_ended)
        self.server.voice_client.source.volume = 0.5


class Servers(defaultdict):
    def __init__(self, bot):
        self.__discordpy_bot = bot
        super().__init__()

    def __missing__(self, key):
        self[key] = new = Server(self.__discordpy_bot, key)
        return new


def get_voice_client(bot, sid):
    """ Fetch voice client for current a given serverid """
    return next(iter([vc for vc in bot.voice_clients if vc.guild.id == sid]), None)


def get_user_voice_channel(ctx):
    """ Get command author voice channel """
    return next(
        iter(
            [
                member.voice.channel
                for member in ctx.guild.members
                if member == ctx.message.author and member.voice is not None
            ]
        ),
        None,
    )
