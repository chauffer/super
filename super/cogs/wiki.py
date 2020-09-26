from base64 import b64encode
from html import unescape

import aiohttp

from aiocache import Cache, cached
from discord.ext import commands
from super.utils import R, wiki


class Wiki(commands.Cog):
    """Wikipedia search"""

    def __init__(self, bot):
        self.bot = bot
        self.wiki = wiki.Wiki()

    @commands.command(no_pm=True, pass_context=True)
    async def w(self, ctx):
        """**.w** - Wikipedia Search - repeat the command for the next result"""
        return await self.wiki.w(ctx)


def setup(bot):
    bot.add_cog(Wiki(bot))
