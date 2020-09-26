import time
import aiohttp
from discord import Embed
import structlog
from super.utils import fuz, owoify

logger = structlog.getLogger(__name__)


class Astro:
    def __init__(self):
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
        self.help = "\n".join(
            [
                "**.astro** <sign> [today|week|month|year] - Daily dose of bullshit",
                "**.astrowo** <sign> [today|week|month|year] - Daiwy dose of buwwshit",
            ]
        )

    async def get_sunsign(self, sunsign, when):
        logger.debug("utils/astro/get_sunsign: Fetching", sunsign=sunsign, when=when)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.api.format(sunsign=sunsign, when=when),
                params={"t": int(time.time())},
                timeout=5,
            ) as resp:
                return await resp.json()

    async def get_horoscope(self, msg, owo=False):
        sunsign = fuz(msg[1], self.sunsigns, threshold=1)
        when = fuz(msg[2] if len(msg) >= 3 else "today", self.times, "today")

        title = f"{when}'s horoscope for {sunsign}"
        horoscope = (await self.get_sunsign(sunsign, when))["horoscope"]
        logger.info("utils/astro/astro: Fetched", sunsign=sunsign)
        if owo:
            horoscope = owoify(horoscope)
            title = owoify(title)

        return (title, horoscope)

    async def chat(self, ctx, owo=False):
        async with ctx.message.channel.typing():
            msg = ctx.message.content.split()
            if len(msg) >= 2:
                title, description = await self.get_horoscope(msg, owo)
                return await ctx.message.channel.send(
                    embed=Embed(title=title, description=description)
                )
            else:
                return await ctx.message.channel.send(
                    embed=Embed(title="Command Help", description=self.help)
                )
