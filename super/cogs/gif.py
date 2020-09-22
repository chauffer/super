import aiohttp
from discord.ext import commands
import structlog

from super.utils import gif


logger = structlog.getLogger(__name__)


class Gif(commands.Cog):
    """Gif"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __exit__(self):
        self.session.close()

    @commands.command(no_pm=True, pass_context=True)
    async def gif(self, ctx):
        """**.gif** <query> - random gif"""
        async with ctx.message.channel.typing():
            text = ctx.message.content.split(" ", 1)[1]
            url = await gif.get_url(self.session, text)
            return await ctx.message.channel.send(f"**{text}**: {url}")


def setup(bot):
    bot.add_cog(Gif(bot))
