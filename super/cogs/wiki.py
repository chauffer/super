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

    def __exit__(self):
        self.session.close()

    @commands.command(no_pm=True, pass_context=True)
    async def w(self, ctx):
        """**.w** - Wikipedia Search - repeat the command for the next result"""
        async with ctx.message.channel.typing():
            words = ctx.message.content.split()[1:]
            slug = (
                "w",
                b64encode(" ".join(words).encode()).decode(),
                ctx.message.channel.id,
            )
            k = await R.incr(slug, 3600) - 1

            return await ctx.message.channel.send(self.wiki.search(words, k))


def setup(bot):
    bot.add_cog(Wiki(bot))
