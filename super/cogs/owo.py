from discord.ext import commands
from super.utils import owo


class Owo(commands.Cog):
    """owo"""

    def __init__(self, bot):
        self.bot = bot
        self.owo = owo.Owo()

    @commands.command(pass_context=True)
    async def owo(self, ctx):
        """**.owo** <text> - owoifier"""
        return await self.owo.owo(ctx)


def setup(bot):
    bot.add_cog(Owo(bot))
