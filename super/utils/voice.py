import asyncio
import html
import math
import os
import re
import tempfile
from collections import defaultdict
from contextlib import suppress
from time import time

from ago import human

import aniso8601
import discord
import youtube_dl
from super.settings import SUPER_HELP_COLOR
from super.settings import SUPER_QUEUE_PAGINATION as S_Q_P
from super.settings import SUPER_YOUTUBE_API_KEY
from super.utils.youtube import YT


class Server:
    def __init__(self, bot, serverid):
        self.bot = bot
        self.id = serverid
        self.channel = None
        self._queue = []
        self.playing = None
        self._volume = 70

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
        await song.get_metadata()

        if song.metadata['snippet']['liveBroadcastContent'] != 'none':
            return await song.channel.send("cannot queue livestreams")

        self._queue.append(song)
        if not self.is_playing:
            return await self.play_next()

        await song.display_queued()
        self.prefetch()

    async def current_song(self, ctx):
        return await ctx.message.channel.send(embed=self.playing.now_playing_embed)

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
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        with suppress(Exception):
            self.voice_client.source.volume = value / 100

    @property
    def _queuepages(self):
        return math.ceil(len(self._queue) / S_Q_P)

    def _queuep(self, page):
        """returns paginated queue"""
        return self._queue[(page - 1) * S_Q_P : page * S_Q_P]

    async def connect(self):
        if self.channel and not self.is_connected:
            await self.channel.connect(timeout=3, reconnect=True)

    async def disconnect(self):
        return await self.voice_client.disconnect()

    async def resume(self):
        return await self.voice_client.resume()

    async def pause(self):
        return await self.voice_client.pause()

    def prefetch(self):
        if self._queue:
            self._queue[0].download()

    async def play_next(self):
        if not self._queue:
            return

        if self.playing:
            self.playing.remove()

        self.playing = self._queue.pop(0)
        print("Connecting")
        await self.playing.play()
        self.prefetch()

    async def display_queue(self, ctx, page):
        if not self._queue:
            return await ctx.message.channel.send("nothing's queued")

        embed = discord.Embed(type="rich", color=SUPER_HELP_COLOR)
        embed.set_author(name="Song Queue")

        [
            embed.add_field(
                name=f"**{index}.** {song.title_duration}", value="\u200b", inline=False
            )
            for index, song in enumerate(self._queuep(page), start=1)
        ]

        embed.set_footer(text=f"page {page} of {self._queuepages}")

        return await ctx.message.channel.send(embed=embed)


class Song:
    """Song object"""

    def __init__(self, url, server, ctx):
        self.url = url
        self.server = server
        self.channel = ctx.message.channel
        self.user = ctx.message.author
        self.bot = ctx.bot

        self.metadata = None
        self.path = (
            os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))
            + ".mp3"
        )
        self.is_downloaded = False
        self.added_at = time()

    def __str__(self):
        return f"**{self.url}** added {self.ago} by {self.user.name}"

    @property
    def ago(self):
        return human(self.added_at, precision=2)

    @property
    def is_playing(self):
        return self.server.is_playing and self.server.playing == self

    @property
    def title(self):
        return self.metadata["snippet"]["title"]

    @property
    def title_duration(self):
        return (
            f"{self.title}"
            f" [{aniso8601.parse_duration(self.metadata['contentDetails']['duration'])}]"
        )

    @property
    def uploader(self):
        return self.metadata["snippet"]["channelTitle"]

    @property
    def thumbnail(self):
        try:
            return self.metadata["snippet"]["thumbnails"]["default"]["url"]
        except:
            return "https://i.imgur.com/s4dTtBy.jpg"

    @property
    def video_id(self):
        return re.findall(
            r"youtu(?:.*\/v\/|.*v\=|\.be\/)([A-Za-z0-9_\-]{11})", self.url
        )[0]

    async def get_metadata(self):
        if not self.metadata:
            self.metadata = await YT().metadata(video_id=self.video_id)

    def remove(self):
        self.is_downloaded = False
        with suppress(Exception):
            os.remove(self.path)

    def download(self):
        """ Download song using youtube_dl """
        if self.is_downloaded:
            return
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

    @property
    def now_playing_embed(self):
        embed = discord.Embed(
            title=self.title_duration,
            url=self.url,
            description=f"by {self.user.mention}",
            color=SUPER_HELP_COLOR,
            type="rich",
        )
        embed.set_author(name=f"now playing")
        embed.set_thumbnail(url=self.thumbnail)
        return embed

    async def display_queued(self):
        embed = discord.Embed(
            title=self.title, url=self.url, color=SUPER_HELP_COLOR, type="rich",
        )
        embed.set_author(name=f"queued in position #{len(self.server._queue)}...")
        embed.set_thumbnail(url=self.thumbnail)
        await self.channel.send(embed=embed)

    async def play(self):
        print("Playing", self.path)
        await self.get_metadata()
        await self.channel.send(embed=self.now_playing_embed)
        await self.server.connect()
        self.download()
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(self.path))
        self.server.voice_client.play(source, after=self.server.song_ended)
        self.server.voice_client.source.volume = self.server.volume


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


async def prompt_video_choice(message, ctx):
    """ Prompt user to choose video by reactions """

    reactions = ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣")

    for reaction in reactions:
        await message.add_reaction(emoji=reaction)

    def check(reaction, reactee):
        return ctx.message.author == reactee and str(reaction.emoji) in reactions

    try:
        reaction, _ = await ctx.bot.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        return 0
    else:
        return reactions.index(str(reaction.emoji))
