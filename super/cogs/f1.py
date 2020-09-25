from discord.ext import commands
import structlog
from super.utils import f1
from contextlib import suppress

logger = structlog.getLogger(__name__)


class F1(commands.Cog):
    """Formula 1"""

    def __init__(self, bot):
        self.bot = bot
        self.f1 = f1.F1()

    @commands.command(pass_context=True)
    async def f1(self, ctx):
        """**.f1** - Formula 1 sessions this weekend"""
        async with ctx.message.channel.typing():
            return await self.f1.f1(ctx.message.content)

    @commands.command(pass_context=True)
    async def f1ns(self, ctx):
        """**.f1ns** - Formula 1 next session"""
        async with ctx.message.channel.typing():
            return await self.f1.f1ns(ctx.message.content)

    @commands.command(pass_context=True)
    async def f1ls(self, ctx):
        """**.f1ls** [page] - Formula 1 list sessions"""
        async with ctx.message.channel.typing():
            return await self.f1.f1ls(ctx.message.content)


def setup(bot):
    bot.add_cog(F1(bot))
