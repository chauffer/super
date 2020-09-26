from discord.ext import commands
import structlog
from super.utils import fuz, owoify, astro

logger = structlog.getLogger(__name__)


class Astro(commands.Cog):
    """Horoscope"""

    def __init__(self, bot):
        self.bot = bot
        self.astro = astro.Astro()

    @commands.command(no_pm=True, pass_context=True)
    async def astro(self, ctx):
        """**.astro** <sign> [today|week|month|year] - Daily dose of bullshit"""
        return await self.astro.chat(ctx)

    @commands.command(no_pm=True, pass_context=True)
    async def astrowo(self, ctx):
        """**.astrowo** <sign> [today|week|month|year] - Daiwy dose of buwwshit"""
        return await self.astro.chat(ctx, True)


def setup(bot):
    bot.add_cog(Astro(bot))
