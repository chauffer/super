from discord.ext import commands
import structlog
from super.utils import fuz, owoify, astro

logger = structlog.getLogger(__name__)


class Astro(commands.Cog):
    """Horoscope"""

    def __init__(self, bot):
        self.bot = bot

    async def _astro(self, ctx, owo=False):
        async with ctx.message.channel.typing():
            message = ctx.message.content.split(" ")

            if len(message) >= 2:
                return await ctx.message.channel.send(
                    embed=(await astro.get_horoscope(message, owo))
                )
            else:
                return await ctx.message.channel.send(
                    ".astro <sign> [**today**|week|month|year]"
                )

    @commands.command(no_pm=True, pass_context=True)
    async def astro(self, ctx):
        """**.astro** <sign> [today|week|month|year] - Daily dose of bullshit"""
        await self._astro(ctx, owo=False)
        return

    @commands.command(no_pm=True, pass_context=True)
    async def astrowo(self, ctx):
        """**.astrowo** <sign> [today|week|month|year] - Daiwy dose of buwwshit"""
        await self._astro(ctx, owo=True)
        return


def setup(bot):
    bot.add_cog(Astro(bot))
