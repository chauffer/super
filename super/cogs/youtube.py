import html
import re
import traceback
from contextlib import suppress

import aniso8601
import discord
import structlog
from discord.ext import commands
from fuzzywuzzy import process
from super.settings import SUPER_QUEUE_PAGINATION, SUPER_MAX_YOUTUBE_LENGTH
from super.utils import get_user_voice_channel, prompt_video_choice
from super.utils.voice import Servers, Song
from super.utils.youtube import YT

logger = structlog.getLogger(__name__)


class Youtube(commands.Cog):
    """Youtube player"""

    def __init__(self, bot):
        self.bot = bot
        self.commands = {
            "pause": (self.pause, ("pause", "stop")),
            "play": (self.resume, ("play", "resume", "start")),
            "leave": (self.leave, ("leave", "quit")),
            "skip": (self.skip, ("next", "skip")),
            "volume": (self.volume, ("volume", "v")),
            "queue": (self.queue, ("queue", "q")),
            "np": (self.np, ("np", "playing")),
            "remove": (self.remove, ("rm", "del", "delete", "remove")),
            "mute": (self.mute, ("mute",)),
            "search": (self.search, ("search", "s")),
        }
        self.S = Servers(self.bot)

    @property
    def words(self):
        words = {}
        for command, info in self.commands.items():
            for word in info[1]:
                words[word] = command
        return words

    def word(self, badword, threshold=90, default=None):
        words = [word for word in self.words.keys() if len(word) > 3]
        candidate, score = process.extractOne(badword, words)
        return self.words[candidate] if score > threshold else default

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
            if self.S[ctx.message.guild.id].is_connected:
                return await self.S[ctx.message.guild.id].disconnect()
        except:
            logger.error(
                "cogs/youtube/leave: Error", error=traceback.format_exc(), server=server
            )
            return await ctx.message.channel.send(":nerd:\n " + traceback.format_exc())

    async def volume(self, ctx, server, message):
        if not message:
            return await ctx.message.channel.send(f"volume: **{str(server.volume)}**")
        try:
            assert 0 <= float(message[0]) <= 0.75
            server.volume = float(message[0])
            logger.info(
                "cogs/youtube/volume: Volume changed",
                volume=server.volume,
                server=server,
            )
        except:
            logger.error(
                "cogs/youtube/volume: Volume change failed",
                error=traceback.format_exc(),
                server=server,
            )
            return await ctx.message.channel.send(":nerd:\n " + traceback.format_exc())
        return await self.bot.add_reaction(ctx.message, ":ok:")

    async def skip(self, ctx, server, message):
        try:
            server.voice_client.stop()
            await ctx.message.channel.send("skipping")
            logger.info(
                "cogs/youtube/skip: Skipped song",
                song=server.playing.url,
                server=server,
            )
            await server.play_next()
        except:
            logger.error(
                "cogs/youtube/skip: Unable to skip song",
                error=traceback.format_exc(),
                server=server,
            )
            return await ctx.message.channel.send(":nerd:\n " + traceback.format_exc())

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
            logger.error(
                "cogs/youtube/np: Error", error=traceback.format_exc(), server=server
            )
            return await ctx.message.channel.send(":nerd:\n " + traceback.format_exc())

    async def search(self, ctx, server, message, lucky=False):
        if not len(message):
            return

        results = await YT().search_videos(" ".join(message), 10)

        if not results:
            return await ctx.message.channel.send("cannot find video")

        if lucky:
            url = "https://youtube.com/watch?v=" + results[0]["id"]
            await server.queue(Song(url, server, ctx))
            return

        embed = discord.Embed()
        embed.set_author(name="here you go...")

        for index, video in enumerate(results):
            embed.add_field(
                name=(
                    f"{index + 1}. {html.unescape(video['snippet']['title'])}"
                    f" [{aniso8601.parse_duration(video['contentDetails']['duration'])}]"
                ),
                value=video["snippet"]["channelTitle"],
                inline=False,
            )

        message = await ctx.message.channel.send(embed=embed)
        logger.debug(
            "cogs/youtube/search: Prompting user for video choice", server=server
        )
        choice = await prompt_video_choice(message, ctx, len(results[:5]))
        await message.delete()
        await server.queue(
            Song("https://youtube.com/watch?v=" + results[choice]["id"], server, ctx)
        )

    async def remove(self, ctx, server, message):
        pos = int(message[0])

        assert 1 <= pos <= 1337

        if server._queue[pos - 1].user != ctx.message.author:
            return await ctx.message.channel.send("you cannot delete this song")

        server._queue.pop(pos - 1)
        logger.info("cogs/youtube/remove: Removed", pos=pos, server=server)
        return await ctx.message.channel.send("deleted")

    async def mute(self, ctx, server, message):
        return await self.volume(ctx, server, ["0"])

    @commands.command(no_pm=True, pass_context=True)
    async def yt(self, ctx):
        """**.yt** <url> - play Youtube video"""
        message = ctx.message.content.split()
        server = self.S[ctx.message.guild.id]

        # empty message
        if len(message) < 2:
            return await ctx.message.channel.send(
                """yotoob
            **.yt <query or url>** to add songs
            **.yt <play|pause|skip>**
            **.yt leave** to leave the channel
            **.yt skip** to skip to the next song
            **.yt volume 0-100** to change volume
            **.yt queue** to list all queued songs
            **.yt np** to see what's playing
            **.yt search** if you want to be more picky with your search
            **.yt rm** remove song from the queue
            **.yt mute** mute the audio
            """
            )

        if not get_user_voice_channel(ctx):
            return await ctx.message.channel.send("join a voice channel first...")

        if server.is_connected and server.channel != get_user_voice_channel(ctx):
            return await ctx.message.channel.send("join MY voice channel....")

        if not server.is_connected:
            server._initial_channel = get_user_voice_channel(ctx)
        # .yt http..
        # this comes before checking for subcommands
        # so if any subcommands need links, this will block them from working
        yt_videoid = re.findall(
            r"youtu(?:.*\/v\/|.*v\=|\.be\/)([A-Za-z0-9_\-]{11})",
            " ".join(message),
        )
        if yt_videoid is not None and len(yt_videoid):
            logger.info("cogs/youtube/yt: Queueing", video_id=yt_videoid, server=server)
            return await server.queue(
                Song("https://youtube.com/watch?v=" + yt_videoid[0], server, ctx)
            )

        # .yt volume 30
        if message[1] in self.words.keys():
            return await self.command(self.words[message[1]])(ctx, server, message[2:])

        # .yt valume 30
        fuzzy_input = " ".join(message[1:])
        good_word = self.word(fuzzy_input)
        if len(fuzzy_input) > 5 and good_word is not None and good_word != message[1]:
            await ctx.message.channel.send(
                f"{message[1]}? assuming you meant _{good_word}_..."
            )
            return await self.command(good_word)(ctx, server, message[2:])

        return await self.search(ctx, server, message[1:], lucky=True)


def setup(bot):
    discord.opus.load_opus("libopus.so.0")
    bot.add_cog(Youtube(bot))
