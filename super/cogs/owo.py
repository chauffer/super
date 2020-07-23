from discord.ext import commands
from super import utils


class Owo(commands.Cog):
    """owo"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def owo(self, ctx):
        """**.owo** <text> - owoifier"""
        async with ctx.message.channel.typing():
            if len(ctx.message.content.split()) == 1:
                return await ctx.message.channel.send("uwu")
            return await ctx.message.channel.send(
                utils.owoify(" ".join(ctx.message.content.split()[1:]))
            )


def setup(bot):
    bot.add_cog(Owo(bot))
