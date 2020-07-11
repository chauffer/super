from __future__ import unicode_literals
import time
import aiohttp
from discord.ext import commands
from discord.utils import get
import discord
import pafy
import os
from super.settings import SUPER_AUDIO_PATH
import youtube_dl
import asyncio


class Song:
    """Song object"""
    def __init__(self,url):
        video = pafy.new(url)
        self.url = url
        self.title = video.title
    
    def __str__(self):
        return self.url


class Youtube(commands.Cog):
    """Youtube player"""

    def __init__(self, bot):
        self.bot = bot
        self.cur_song = None
        self.queue = []


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
            ydl.download([self.cur_song.url])


    async def fetch_next_song(self, after):
        """ Remove downloaded song """
        os.remove(f'data/music/{self.cur_song.title}.mp3')


    async def _play_song(self, song, voice_client):
        """ Download and play the song """
        self.cur_song = song
        await self.download_song()
        audio_source = discord.FFmpegPCMAudio(f'data/music/{self.cur_song.title}.mp3')
        voice_client.play(audio_source, after=self.fetch_next_song)
    

    async def _get_voice_client(self, ctx):
        """ Fetch voice client for current server """
        for client in self.bot.voice_clients:
            if client.guild == ctx.guild:
                return client
        return None


    async def _init_play_song(self, song, voice_client):
        """ If no song is playing or is not paused, play a new one, otherwise append to queue """
        if voice_client.is_playing() or voice_client.is_paused():
            self.queue.append(song)
        else:
            await self._play_song(song, voice_client)


    @commands.command(no_pm=True, pass_context=True)
    async def play(self, ctx):
        """**.play** <url> - play Youtube video"""
        voice_client = self._get_voice_client
        if voice_client is None:
            if ctx.message.author.voice.channel == None:
                return await ctx.message.channel.send('Join a vc first.')
            voice_client = await ctx.message.author.voice.channel.join()

        song = Song(ctx.message.content.split(" ", 1)[1])
        await self._init_play_song(song, voice_client)
        

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
