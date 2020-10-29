
import random
from time import time

from ago import human

from discord.ext import commands
from super import utils


class Uptime(commands.Cog):
    """Uptime"""

    def __init__(self, bot):
        self.bot = bot
        self.start = time()

    @commands.command(pass_context=True)
    async def uptime(self, ctx):
        """**.uptime** - show Super's uptime"""
        diff = time() - self.start
        this_long = human(self.start, precision=3).replace('ago', '').strip()
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(
                f"i've been awake for {this_long}..."
            )

def setup(bot):
    bot.add_cog(Uptime(bot))
