from discord.ext import commands
from super.utils import eightball


class Eightball(commands.Cog):
    """Eightball"""

    def __init__(self, bot):
        self.bot = bot
        self.eightball = eightball.Eightball()

    @commands.command(pass_context=True, name="8ball")
    async def eightball(self, ctx):
        """**.8ball** <question> - For life's most troubling issues"""
        return await self.eightball.eightball(ctx)


def setup(bot):
    bot.add_cog(Eightball(bot))
