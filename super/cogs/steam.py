import random

import aiohttp

from aiocache import Cache, cached
from discord.ext import commands
from super import utils
from super.utils import R, fuz


class Steam(commands.Cog):
    """Steam"""

    def __init__(self, bot):
        self.bot = bot
        self.api = "https://api.steampowered.com/ISteamApps/GetAppList/v0002/"
        self.link = "https://store.steampowered.com/app/"

    @cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
    async def games(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api, timeout=5) as r:
                return {
                    game["appid"]: game["name"]
                    for game in (await r.json())["applist"]["apps"]
                }

    @cached(cache=Cache.REDIS, ttl=86400, endpoint=R.host, port=R.port)
    async def fuzzy_match(self, text):
        games = await self.games()
        game = fuz(text, list(games.values()), default=False)
        if not game:
            return False
        return list(games.keys())[list(games.values()).index(game)]

    @commands.command(pass_context=True)
    async def steam(self, ctx):
        """**.steam** <name> - Show the store page for a game"""
        async with ctx.message.channel.typing():
            if len(ctx.message.content.split()) == 1:
                return await ctx.message.channel.send("Usage: .steam <name>")

            match = await self.fuzzy_match(ctx.message.content.split(" ", 1)[1])
            if match:
                return await ctx.message.channel.send(self.link + str(match))

            else:
                return await ctx.message.channel.send("no game found :(")


def setup(bot):
    bot.add_cog(Steam(bot))
