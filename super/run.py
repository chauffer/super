from discord.ext import commands
import discord
import structlog

from . import settings
from .utils import R

description = "<https://github.com/chauffer/super|super>"

bot = commands.Bot(
    command_prefix=settings.SUPER_PREFIX,
    description=description,
    pm_help=None,
    intents=discord.Intents.all(),
)

logger = structlog.getLogger("super")

extensions = [
    "super.cogs.np",
    "super.cogs.markov",
    "super.cogs.translate",
    "super.cogs.gif",
    "super.cogs.ping",
    "super.cogs.eightball",
    "super.cogs.f1",
    "super.cogs.astro",
    "super.cogs.help",
    "super.cogs.owo",
    "super.cogs.youtube",
    "super.cogs.wiki",
    "super.cogs.uptime",
    "super.cogs.steam",
    "super.cogs.screenshot",
]


@bot.event
async def on_ready():
    logger.info("super/on_ready: Ready!")


def main():
    for extension in extensions:
        try:
            bot.load_extension(extension)
            logger.debug("super/load_cogs: Loaded", extension=extension)
        except Exception as e:
            logger.error(
                "super/load_cogs: Failed to load",
                extension=extension,
                err_type=type(e).__name__,
                err=e,
            )

    bot.run(settings.SUPER_DISCORD_TOKEN)


if __name__ == "__main__":
    main()
