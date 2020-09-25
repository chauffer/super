from discord import Embed
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
        async with ctx.message.channel.typing():
            (title, content) = await self.astro.chat(ctx.message.content, False)
            return await ctx.message.send(embed=Embed(title=title, description=content))

    @commands.command(no_pm=True, pass_context=True)
    async def astrowo(self, ctx):
        """**.astrowo** <sign> [today|week|month|year] - Daiwy dose of buwwshit"""
        async with ctx.message.channel.typing():
            (title, content) = await self.astro.chat(ctx.message.content, False)
            return await ctx.message.send(embed=Embed(title=title, description=content))


def setup(bot):
    bot.add_cog(Astro(bot))
