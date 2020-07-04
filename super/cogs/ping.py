import time
from discord.ext import commands


class Ping(commands.Cog):
    """Connection diagnostics"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """**.ping** - Benchmark for the bot to send & edit a message"""
        before = time.time()
        msg = await ctx.message.channel.send("1/3 .")
        await msg.edit(content="2/3 ..")
        benchmark = int((time.time() - before) * 1000)
        await msg.edit(content=f"3/3 ... {benchmark}ms")


def setup(bot):
    bot.add_cog(Ping(bot))
