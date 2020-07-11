from discord.ext import commands
import discord
import aiohttp
import json
import asyncio
import uvloop
import ctypes
import ctypes.util

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from . import settings
from .utils import R


description = "<https://github.com/chauffer/super|super>"

bot = commands.Bot(
    command_prefix=settings.SUPER_PREFIX, description=description, pm_help=None
)

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
    "super.cogs.youtube",
]


@bot.event
async def on_ready():
    print("Super ready!")


def main():
    discord.opus.load_opus('libopus.so.0')
    if not discord.opus.is_loaded():
        print("OPUS NOT LOADED")
    for extension in extensions:
        try:
            bot.load_extension(extension)
            print(f"Loaded {extension}")
        except Exception as e:
            print(
                "Failed to load extension {}\n{}: {}".format(
                    extension, type(e).__name__, e
                )
            )

    bot.run(settings.SUPER_DISCORD_TOKEN)


if __name__ == "__main__":
    main()
