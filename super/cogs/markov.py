import os
import random
import re
from discord.ext import commands
from cobe.brain import Brain
from super import settings
from super.utils import R, owoify, markov


class Markov(commands.Cog):
    """Random message"""

    def __init__(self, bot):
        self.bot = bot
        self.markov = markov.Markov()
        os.makedirs("/data/cobe/", exist_ok=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        return await self.markov.reply(message, self.bot.user.id)

    @commands.command(no_pm=True, pass_context=True)
    async def chat(self, ctx):
        """**.chat** <text> - Reply to a message"""
        return await self.markov.chat(ctx)

    @commands.command(no_pm=True, pass_context=True)
    async def owochat(self, ctx):
        """**.owochat** <text> - Reply to a message, owoified"""
        return await self.markov.chat(ctx, True)

    @commands.command(no_pm=True, pass_context=True)
    async def replyrate(self, ctx):
        return await self.markov.replyrate(ctx)


def setup(bot):
    bot.add_cog(Markov(bot))
