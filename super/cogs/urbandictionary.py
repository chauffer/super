from base64 import b64encode
from html import unescape

import aiohttp

from aiocache import Cache, cached
from discord.ext import commands
from super.utils import R


class Urbandictionary(commands.Cog):
    """Urbandictionarypedia search"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.url = "https://api.urbandictionary.com/v0/define

    def __exit__(self):
        self.session.close()

    @cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
    async def word(self, word):
        async with self.session.get(self.url, params={"term": word) as r:
            return (await r.json())["list"]

    @cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
    async def Urbandictionary(self, query, offset=0):
        async with self.session.get(
            self.url,
            params={
                "action": "query",
                "list": "search",
                "format": "json",
                "srsearch": query,
                "sroffset": offset,
            },
        ) as response:
            return (await response.json())["query"]["search"]

    @commands.command(no_pm=True, pass_context=True)
    async def w(self, ctx):
        """**.w** - Urbandictionarypedia Search - repeat the command for the next result"""
        async with ctx.message.channel.typing():
            words = ctx.message.content.split()[1:]
            slug = (
                "w",
                b64encode(" ".join(words).encode()).decode(),
                ctx.message.channel.id,
            )
            k = await R.incr(slug, 3600) - 1

            try:
                result = (await self.Urbandictionary(words, 10 * (k // 10)))[k % 10]
            except IndexError:
                return await ctx.message.channel.send("?")

            return await ctx.message.channel.send(await self._get_url(result["title"]))


def setup(bot):
    bot.add_cog(Urbandictionary(bot))
