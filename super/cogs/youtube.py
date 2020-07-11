import traceback
from contextlib import suppress

import discord
from discord.ext import commands
from fuzzywuzzy import process
from super.settings import SUPER_QUEUE_PAGINATION
from super.utils import get_user_voice_channel
from super.utils.voice import Servers, Song


class Youtube(commands.Cog):
    """Youtube player"""

    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            "pause": (self.pause, ("pause",)),
            "play": (self.resume, ("play", "resume", "start")),
            "leave": (self.leave, ("leave", "quit")),
            "skip": (self.skip, ("next", "skip")),
            "volume": (self.volume, ("volume", "v")),
            "queue": (self.queue, ("queue", "q")),
            "np": (self.np, ("np", "playing")),
        }
        self.S = Servers(self.bot)

    @property
    def words(self):
        words = {}
        for command, info in self.commands.items():
            for word in info[1]:
                words[word] = command
        return words

    def word(self, badword):
        result = process.extract(badword, self.words.keys(), limit=30)
        return next(iter([v for k, v in self.words.items() if k == result[0][0]]), None)

    def command(self, word):
        return self.commands[word][0]

    async def resume(self, ctx, server, message):
        """**.yt resume** - resume current song"""
        if not server.voice_client:
            return await ctx.message.channel.send("nothing is playing")

        return server.resume()

    async def pause(self, ctx, server, message):
        """**.yt pause** - pause current song"""

        if not server.voice_client:
            return await ctx.message.channel.send("nothing is playing")

        return server.pause()

    async def leave(self, ctx, server, message):
        try:
            return await self.S[ctx.message.guild.id].disconnect()
        except:
            return await ctx.message.channel.send(
                ":thinking:\n " + traceback.format_exc()
            )

    async def volume(self, ctx, server, message):
        if not message:
            return await ctx.message.channel.send(
                "volume: **" + str(int(server.voice_client.source.volume * 100)) + "**"
            )
        try:
            volume = int(message[0])
            assert 0 <= volume <= 100
            server.voice_client.source.volume = volume / 100
        except:
            return await ctx.message.channel.send(
                ":thinking:\n " + traceback.format_exc()
            )

    async def skip(self, ctx, server, message):
        try:
            server.voice_client.stop()
            await server.play_next()
            return await ctx.message.channel.send("skipped")
        except:
            return await ctx.message.channel.send(
                ":thinking:\n " + traceback.format_exc()
            )

    async def queue(self, ctx, server, message):
        page = 1
        with suppress(Exception):
            page = int(message[0])
            assert 1 <= page <= server._queuepages
        return await server.display_queue(ctx, page)

    async def np(self, ctx, server, message):
        try:
            return await server.current_song(ctx)
        except:
            return await ctx.message.channel.send(
                ":thinking:\n " + traceback.format_exc()
            )

    @commands.command(no_pm=True, pass_context=True)
    async def yt(self, ctx):
        """**.yt** <url> - play Youtube video"""
        message = ctx.message.content.split(" ")
        server = self.S[ctx.message.guild.id]

        if not message[1:]:
            return await ctx.message.channel.send(
                """yotoob
            **.yt <youtubelink>** to add songs
            **.yt pause** to pause
            **.yt <play|resume|start>** to play
            **.yt leave** to leave the channel
            **.yt skip** to skip to the next song
            **.yt volume 0-100** to change volume
            **.yt queue** to list all queued songs
            **.yt np** to show currently playing song
            """
            )

        if not get_user_voice_channel(ctx):
            return await ctx.message.channel.send("join a voice channel first...")

        if server.is_connected and server.channel != get_user_voice_channel(ctx):
            return await ctx.message.channel.send("join MY voice channel....")

        if message[1].startswith("http"):
            if not server.is_connected:
                server.channel = get_user_voice_channel(ctx)
                await server.connect()
            return await server.queue(Song(message[1], server, ctx.message))

        good_word = self.word(message[1])
        if good_word != message[1]:
            await ctx.message.channel.send(
                f"{message[2]}? assuming you meant _{good_word}_..."
            )
        return await self.command(good_word)(ctx, server, message[2:])


def setup(bot):
    discord.opus.load_opus("libopus.so.0")
    bot.add_cog(Youtube(bot))
