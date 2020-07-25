import os
import re
import tempfile
import asyncio
import math
import html
from collections import defaultdict
from contextlib import suppress
from time import time
import youtube_dl
import discord
from super.settings import (
    SUPER_HELP_COLOR,
    SUPER_YOUTUBE_API_KEY,
    SUPER_QUEUE_PAGINATION as S_Q_P,
)
from ago import human
from aioyoutube import Api
import aniso8601


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

    async def queue(self, query, server, message):
        query = " ".join(query)

        if "list" in query:
            return await message.channel.send("Playlists are not supported.")

        song = Song(query, server, message, self.bot)
        await song.get_metadata()
        self._queue.append(song)
        if not self.is_playing:
            return await self.play_next()
        return await song.display_queued(len(self._queue))

    async def current_song(self, ctx):
        embed = discord.Embed(type="rich", color=SUPER_HELP_COLOR)
        embed.set_author(name="now playing")
        embed.add_field(
            name=self.playing.title,
            value=f"by {self.playing.user.mention}",
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
        """returns paginated queue"""
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

    def __init__(self, query, server, message, bot):
        self.bot = bot
        self.query = query
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
        self.api = Api()

    def __str__(self):
        return f"**{self.query}** added {self.ago} by {self.user.name}"

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
        return self.metadata["snippet"]["thumbnails"]["standard"]["url"]

    def remove(self):
        self.is_downloaded = False
        with suppress(Exception):
            os.remove(self.path)

    async def prompt_video_choice(self, message):
        """ Prompt user to choose video by reactions """

        reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

        for reaction in reactions:
            await message.add_reaction(emoji=reaction)

        def check(reaction, user):
            return user == self.user and str(reaction.emoji) in reactions

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=60.0, check=check
            )
        except asyncio.TimeoutError:
            return 0
        else:
            return reactions.index(str(reaction.emoji))

    async def fetch_videos(self):
        """ Fetch videos based on query """
        search = self.api.search(
            key=SUPER_YOUTUBE_API_KEY, text=self.query, max_results=5
        )

        result = await search

        search = self.api.videos(
            key=SUPER_YOUTUBE_API_KEY,
            video_ids=[video["id"]["videoId"] for video in result["items"]],
            part=["snippet", "contentDetails"],
        )

        metadatas = await search

        embed = discord.Embed(title="pick video by reacting to this message")
        embed.set_author(name="here you go...")

        for index, video in enumerate(metadatas["items"]):
            embed.add_field(
                name=(
                    f"{index + 1}. {html.unescape(video['snippet']['title'])}"
                    f" [{aniso8601.parse_duration(video['contentDetails']['duration'])}]"
                ),
                value=video["snippet"]["channelTitle"],
                inline=False,
            )

        msg = await self.channel.send(embed=embed)
        choice = await self.prompt_video_choice(msg)

        self.query = result["items"][choice]["id"]["videoId"]
        self.metadata = metadatas["items"][choice]

        await msg.delete()

    async def get_metadata(self):
        """ Fetch song metadata using aioyoutube """

        if "https" not in self.query:
            await self.fetch_videos()
        else:
            self.query = self.query.split("?v=", 1)[1]
            search = self.api.videos(
                key=SUPER_YOUTUBE_API_KEY,
                video_ids=[self.query],
                part=["snippet", "contentDetails"],
            )
            result = await search
            self.metadata = result["items"][0]

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
            ydl.download([self.query])
            self.is_downloaded = True

    async def now_playing(self):
        embed = discord.Embed(
            title=self.title_duration,
            url=f"https://www.youtube.com/watch?v={self.query}",
            description=f"by {self.user.mention}",
            color=SUPER_HELP_COLOR,
            type="rich",
        )
        embed.set_author(name=f"now playing")
        embed.set_thumbnail(url=self.thumbnail)
        await self.channel.send(embed=embed)

    async def display_queued(self, index):
        embed = discord.Embed(
            title=self.title,
            url=f"https://www.youtube.com/watch?v={self.query}",
            color=SUPER_HELP_COLOR,
            type="rich",
        )
        embed.set_author(name=f"queued in position #{index}...")
        embed.set_thumbnail(url=self.thumbnail)
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
