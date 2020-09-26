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
        self.translate = translate.Translate()

    @commands.command(no_pm=False, pass_context=True, name="t")
    async def t(self, ctx):
        """**.t** [from lang] [to lang] <sentence>. Auto detects by default."""
        return await self.translate.t(ctx)


def setup(bot):
    bot.add_cog(Translate(bot))
