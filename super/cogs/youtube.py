from __future__ import unicode_literals
from discord.ext import commands
from discord.utils import get
import discord
import os
from super.settings import SUPER_AUDIO_PATH
import youtube_dl
from fuzzywuzzy import process


discord.opus.load_opus('libopus.so.0')

class Song:
    """Song object"""
    def __init__(self,url):
        self.url = url
        self.title = None
    
    def __str__(self):
        return self.url


class Youtube(commands.Cog):
    """Youtube player"""

    def __init__(self, bot):
        self.bot = bot
        self.cur_song = None
        self.commands = {
            'pause': (self.pause, ('pause')),
            'play': (self.resume, ('play', 'resume')),
        }


    @property
    def words(self):
        words = {}
        for command, info in self.commands.items():
            for word in info[1]:
                words[word] = command
        return words


    def word(self, badword):
        result = process.extract(badword, self.words.keys(), limit=1)
        return [v for k, v in self.words.items() if k == result[0][0]][0]


    def command(self, word):
        return self.commands[word][0]


    async def download_song(self):
        """ Download song using youtube_dl """
        ydl_opts = {
            'outtmpl': 'data/music/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'verbose': True,
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            metadata = ydl.extract_info(self.cur_song.url, download=True)
            self.cur_song.title = ydl.prepare_filename(metadata)


    def fetch_next_song(self, after):
        """ Remove downloaded song """
        os.remove(self.cur_song.title.replace('.webm', '.mp3'))


    async def _play_song(self, song, voice_client):
        """ Download and play the song """
        self.cur_song = song
        await self.download_song()
        audio_source = discord.FFmpegPCMAudio(self.cur_song.title.replace('.webm', '.mp3'))
        voice_client.play(audio_source, after=self.fetch_next_song)
    

    def _get_voice_client(self, ctx):
        """ Fetch voice client for current server """
        for client in self.bot.voice_clients:
            if client.guild == ctx.guild:
                return client
        return None


    def _get_user_voice_channel(self, ctx):
        """ Get command author voice channel """
        for member in ctx.guild.members:
            if member == ctx.message.author:
                if member.voice != None:
                    return member.voice.channel
                break
        return None


    async def _init_play_song(self, song, voice_client):
        """ If no song is playing or is not paused, play a new one, otherwise append to queue """
        if voice_client.is_playing() or voice_client.is_paused():
            self.queue.append(song)
        else:
            await self._play_song(song, voice_client)


    async def resume(self, ctx):
        """**.yt resume** - resume current song"""
        voice_client = self._get_voice_client(ctx)
        if voice_client is None:
            return await ctx.message.channel.send('There are no stopped songs.')
        await voice_client.resume()


    async def pause(self, ctx):
        """**.yt pause** - pause current song"""
        voice_client = self._get_voice_client(ctx)
        if voice_client is None:
            return await ctx.message.channel.send('Not playing any song.')
        await voice_client.pause()


    @commands.command(no_pm=True, pass_context=True)
    async def yt(self, ctx):
        """**.yt** <url> - play Youtube video"""
        subcommand = ctx.message.content.split(" ", 1)[1]

        if 'https' not in subcommand:
            command = self.command(self.word(subcommand))
            return await command

        voice_channel = self._get_user_voice_channel(ctx)
        if voice_channel is None:
            return await ctx.message.channel.send('Join a Voice Channel first.')
        await voice_channel.connect()

        song = Song(subcommand)
        await self._init_play_song(song, self._get_voice_client(ctx))


    @commands.command(no_pm=True, pass_context=True)
    async def leave(self,ctx):
        """**.leave** - leaves the voice channel"""
        self.context = None
        for client in self.bot.voice_clients:
            if client.guild == ctx.guild:
                self.state = 'INACTIVE'
                return await client.disconnect()


def setup(bot):
    bot.add_cog(Youtube(bot))
