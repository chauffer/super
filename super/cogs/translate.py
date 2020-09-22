from discord.ext import commands
from aiogoogletrans import Translator
from aiogoogletrans.constants import LANGUAGES
import structlog

from super.utils import translate

logger = structlog.getLogger(__name__)


class Translate(commands.Cog):
    """Translator"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(no_pm=False, pass_context=True, name="t")
    async def t(self, ctx):
        """**.t** [from lang] [to lang] <sentence>. Auto detects by default."""
        words = ctx.message.content.split(" ")[1:]
        if not words:
            return await ctx.message.channel.send(
                "**.t** [from lang] [to lang] <sentence>. Auto detects by default."
            )
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(
                await translate.translate(words)
            )


def setup(bot):
    bot.add_cog(Translate(bot))
