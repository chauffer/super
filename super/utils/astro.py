import time
import aiohttp
from discord import Embed
import structlog
from super.utils import fuz, owoify

logger = structlog.getLogger(__name__)

sunsigns = [
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
times = ("today", "week", "month", "year")
api = "http://horoscope-api.herokuapp.com/horoscope/{when}/{sunsign}"

async def get_sunsign(sunsign, when):
    logger.debug("utils/astro/get_sunsign: Fetching", sunsign=sunsign, when=when)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            api.format(sunsign=sunsign, when=when),
            params={"t": int(time.time())},
            timeout=5,
        ) as resp:
            return await resp.json()

async def get_horoscope(msg, owo=False):
    sunsign = fuz(msg[1], sunsigns, threshold=1)
    when = fuz(
        msg[2] if len(msg) >= 3 else "today", times, "today"
    )

    title = f"{when}'s horoscope for {sunsign}"
    horoscope = (await get_sunsign(sunsign, when))["horoscope"]
    logger.info("utils/astro/astro: Fetched", sunsign=sunsign)
    if owo:
        horoscope = owoify(horoscope)
        title = owoify(title)
    
    return Embed(title=title, type="rich", description=horoscope)
