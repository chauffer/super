from base64 import b64encode
from html import unescape

import aiohttp

from aiocache import Cache, cached
from discord.ext import commands
from super.utils import R


class Wiki(commands.Cog):
    """Wikipedia search"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.url = "https://en.wikipedia.org/w/api.php"

    def __exit__(self):
        self.session.close()

    @cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
    async def _get_url(self, title):
        async with self.session.get(
            self.url,
            params={
                "action": "query",
                "prop": "info",
                "format": "json",
                "generator": "allpages",
                "inprop": "url",
                "gapfrom": title,
                "gaplimit": 1,
            },
        ) as r:
            return list((await r.json())["query"]["pages"].items())[0][1]["fullurl"]

    @cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
    async def wiki(self, query, offset=0):
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
        """**.w** - Wikipedia Search - repeat the command for the next result"""
        async with ctx.message.channel.typing():
            words = ctx.message.content.split()[1:]
            slug = (
                "w",
                b64encode(" ".join(words).encode()).decode(),
                ctx.message.channel.id,
            )
            k = await R.incr(slug, 3600) - 1

            try:
                result = (await self.wiki(words, 10 * (k // 10)))[k % 10]
            except IndexError:
                return await ctx.message.channel.send("?")

            return await ctx.message.channel.send(await self._get_url(result["title"]))


def setup(bot):
    bot.add_cog(Wiki(bot))
