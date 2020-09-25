from asyncio import gather
import json
import aiohttp
from discord.ext import commands

from super import settings
from super.utils import R, np


class Np(commands.Cog):
    """Last.fm Songs"""

    def __init__(self, bot):
        self.bot = bot
        self.np = np.Np()

    @commands.command(no_pm=True, pass_context=True)
    async def np(self, ctx):
        """**.np** - Now playing song from last.fm"""
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(self.np.np(ctx))

    @commands.command(no_pm=True, pass_context=True, name="wp")
    async def wp(self, ctx):
        """**.wp** - Now playing, for the whole server"""
        async with ctx.message.channel.typing():
            return await self.np.wp(ctx, ctx.message.guild.members)


def setup(bot):
    bot.add_cog(Np(bot))
