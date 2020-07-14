import os
import tempfile
from collections import defaultdict
from contextlib import suppress
from time import time

from ago import human

import discord
import youtube_dl
import asyncio


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
        self._queue.append(song)
        if not self.is_playing:
            await self.play_next()

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
        self.playing.play()


class Song:
    """Song object"""

    def __init__(self, url, server, user):
        self.url = url
        self.server = server
        self.user = user
        self.title = None
        self.metadata = None
        self.path = (
            os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()))
            + ".mp3"
        )
        self.is_downloaded = False

        self.added_at = time()

    def __str__(self):
        return f"**{self.title}** added {self.ago} by {self.user}"

    @property
    def ago(self):
        return human(self.added_at, precision=2)

    @property
    def is_playing(self):
        return self.server.is_playing and self.server.playing == self

    def remove(self):
        self.is_downloaded = False
        with suppress(Exception):
            os.remove(self.path)

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
            self.metadata = ydl.extract_info(self.url, download=True)
            self.title = self.metadata["title"]
            self.is_downloaded = True

    def play(self):
        if not self.is_downloaded:
            self.download()
        print("Playing", self.path)
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
