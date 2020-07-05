import random
from discord.ext import commands
from super import utils


class Eightball(commands.Cog):
    """Eightball"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name="8ball")
    async def eightball(self, ctx):
        """**.8ball** <question> - For life's most troubling issues"""
        async with ctx.message.channel.typing():
            if len(ctx.message.content.split(" ")) == 1:
                return await ctx.message.channel.send(
                    "I can't read minds. :disappointed:"
                )
            return await ctx.message.channel.send(
                random.choice(utils.eightball_options)
            )


def setup(bot):
    bot.add_cog(Eightball(bot))
