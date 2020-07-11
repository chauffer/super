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
        #self.description = video.description
    
    def __str__(self):
        return self.url


class Youtube(commands.Cog):
    """Youtube player"""

    def __init__(self, bot):
        self.bot = bot
        self.state = 'INACTIVE'
        self.cur_song = None
        self.voice_client = None
        self.audio_source = None
        self.context = None


    async def download_song(self):
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


    async def fetch_next_song(self):
        os.remove(f'data/music/{self.cur_song.title}.mp3')
        self.state = 'WAITING'



    async def _play_song(self, ctx):
        if self.state == 'WAITING':
            self.state = 'PLAYING'
            await self.download_song()
            self.audio_source = discord.FFmpegPCMAudio(f'data/music/{self.cur_song.title}.mp3')
            self.voice_client.play(self.audio_source, after=self.fetch_next_song)

    
    @commands.command(no_pm=True, pass_context=True)
    async def join(self, ctx):
        """**.join** - joins the default voice channel"""
        for channel in ctx.guild.voice_channels:
            if channel.name == 'Music':
                await channel.connect()
                self.voice_client = ctx.voice_client
                self.state = 'WAITING'
                break


    @commands.command(no_pm=True, pass_context=True)
    async def play(self, ctx):
        """**.play** <url> - play Youtube video"""
        self.context = ctx
        if self.state != 'WAITING' and self.state != 'PLAYING':
            return await ctx.message.channel.send('Not in a vc! Use .join command first.')
        self.cur_song = Song(ctx.message.content.split(" ", 1)[1])
        await self._play_song(ctx)
        

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
