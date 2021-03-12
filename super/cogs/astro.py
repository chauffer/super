import random
import time

import aiohttp

import structlog
from discord import Embed
from discord.ext import commands
from super.utils import fuz, owoify, sunsigns, wind_directions

logger = structlog.getLogger(__name__)


class Astro(commands.Cog):
    """Horoscope"""

    def __init__(self, bot):
        self.bot = bot
        self.sunsigns = sunsigns
        self.times = ("today", "yesterday", "tomorrow")
        self.api = "https://aztro.sameerkumar.website/?sign={sunsign}&day={when}"
        self.seed = random.random()

    async def _get_sunsign(self, sunsign, when):
        logger.debug("cogs/astro/_get_sunsign: Fetching", sunsign=sunsign, when=when)
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api.format(sunsign=sunsign, when=when),
                timeout=5,
            ) as resp:
                return await resp.json()

    def _time(self, message):
        return fuz(message[2] if len(message) >= 3 else "today", self.times, "today")

    def _try_truth_mode(self, data):
        horoscope = data["description"]
        random.seed(horoscope)
        truth_mode = random.random() < 0.05
        if truth_mode:
            horoscope = "The stars and planets will not affect your life in any way."
        random.seed(self.seed + time.time())  # a caso
        return truth_mode, horoscope

    def _try_owo(self, owo, string):
        if owo:
            string = owoify(string)
        return string

    def _custom_data(self, data):
        random.seed(data["description"])
        data["preferred_wind"] = random.choice(wind_directions)
        data["losing_lottery_n"] = ", ".join(
            [str(random.randint(1, 50)) for _ in range(0, 5)]
        )
        random.seed(self.seed + time.time())
        return data

    async def _astro(self, ctx, owo=False):
        async with ctx.message.channel.typing():
            message = ctx.message.content.split(" ")

            if len(message) >= 2:
                logger.debug("cogs/astro/_astro: Fetching", message=message[1])
                sunsign = fuz(message[1], self.sunsigns, threshold=1)
            else:
                return await ctx.message.channel.send(
                    ".astro <sign> [**today**|yesterday|tomorrow]"
                )

            when = self._time(message)
            data = await self._get_sunsign(sunsign, when)
            logger.info("cogs/astro/_astro: Fetched", sunsign=sunsign)

            truth_mode, horoscope = self._try_truth_mode(data)
            data = self._custom_data(data)

            e = Embed(
                title=self._try_owo(owo, f"{when}'s horoscope for {sunsign}"),
                description=self._try_owo(owo, horoscope),
                type="rich",
            )

            if not truth_mode:
                for key, value in data.items():
                    if key in ("description", "current_date", "description"):
                        continue
                    key, value = key.lower().replace("_", " "), value.lower()
                    if owo:
                        key, value = self._try_owo(owo, key), self._try_owo(owo, value)
                    e.add_field(name=key, value=value, inline=True)

            return e

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
