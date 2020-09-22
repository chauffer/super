from discord.ext import commands
import structlog
from super.utils import f1
from contextlib import suppress

logger = structlog.getLogger(__name__)


class F1(commands.Cog):
    """Formula 1"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def f1(self, ctx):
        """**.f1** - Formula 1 sessions this weekend"""
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(
                "\n".join(await f1.get_events(weekend=True))
            )

    @commands.command(pass_context=True)
    async def f1ns(self, ctx):
        """**.f1ns** - Formula 1 next session"""
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send("\n".join(await f1.get_events(1)))

    @commands.command(pass_context=True)
    async def f1ls(self, ctx):
        """**.f1ls** [page] - Formula 1 list sessions"""
        page = 1
        if len(ctx.message.content.split()[1:]):
            with suppress(Exception):
                page = int(ctx.message.content.split()[1])

        events = "\n".join(await f1.get_events(page=page, more=True))
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(events)


def setup(bot):
    bot.add_cog(F1(bot))
