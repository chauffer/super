import random
import time

import aiohttp

import structlog
from discord import Embed
from discord.ext import commands
from super.utils import fuz, owoify, superheroes

logger = structlog.getLogger(__name__)


class Astro(commands.Cog):
    """Horoscope"""

    def __init__(self, bot):
        self.bot = bot
        self.sunsigns = [
            "aries",
            "taurus",
            "gemini",
            "cancer",
            "leo",
            "virgo",
            "libra",
            "scorpio",
            "sagittarius",
            "capricorn",
            "aquarius",
            "pisces",
        ]
        self.times = ("today", "week", "month", "year")
        self.api = "http://horoscope-api.herokuapp.com/horoscope/{when}/{sunsign}"
        self.seed = random.random()

    async def _get_sunsign(self, sunsign, when):
        logger.debug("cogs/astro/_get_sunsign: Fetching", sunsign=sunsign, when=when)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.api.format(sunsign=sunsign, when=when),
                params={"t": int(time.time())},
                timeout=5,
            ) as resp:
                return await resp.json()

    async def _astro(self, ctx, owo=False):
        async with ctx.message.channel.typing():
            message = ctx.message.content.split(" ")

            if len(message) >= 2:
                logger.debug("cogs/astro/_astro: Fetching", message=message[1])
                sunsign = fuz(message[1], self.sunsigns, threshold=1)
            else:
                return await ctx.message.channel.send(
                    ".astro <sign> [**today**|week|month|year]"
                )

            when = fuz(
                message[2] if len(message) >= 3 else "today", self.times, "today"
            )

            title = f"{when}'s horoscope for {sunsign}"
            horoscope = (await self._get_sunsign(sunsign, when))["horoscope"]
            random.seed(horoscope)
            horoscope = horoscope.replace('Ganesha', random.choice(superheroes))
            random.seed(self.seed)  # a caso
            logger.info("cogs/astro/_astro: Fetched", sunsign=sunsign)
            if owo:
                horoscope = owoify(horoscope)
                title = owoify(title)

            return Embed(title=title, type="rich", description=horoscope)

    @commands.command(no_pm=True, pass_context=True)
    async def astro(self, ctx):
        """**.astro** <sign> [today|week|month|year] - Daily dose of bullshit"""
        return await ctx.message.channel.send(embed=await self._astro(ctx))

    @commands.command(no_pm=True, pass_context=True)
    async def astrowo(self, ctx):
        """**.astrowo** <sign> [today|week|month|year] - Daiwy dose of buwwshit"""
        return await ctx.message.channel.send(embed=await self._astro(ctx, owo=True))


def setup(bot):
    bot.add_cog(Astro(bot))
