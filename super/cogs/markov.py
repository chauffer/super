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
        if message.author.bot:  # Ignore bots
            return
        if message.content.startswith(settings.SUPER_PREFIX):  # Ignore commands
            return
        return await self.markov.reply(message.content, self.bot.user.id, message.author.guild.id, message.channel.id, message.mentions)

    @commands.command(no_pm=True, pass_context=True)
    async def chat(self, ctx):
        """**.chat** <text> - Reply to a message"""
        msg = ctx.message
        async with msg.channel.typing():
            return await msg.channel.send(self.markov.chat(msg.content.split(" ", 1)[1], msg.author.guild.id))

    @commands.command(no_pm=True, pass_context=True)
    async def owochat(self, ctx):
        """**.owochat** <text> - Reply to a message, owoified"""
        msg = ctx.message
        async with msg.channel.typing():
            return await msg.channel.send(self.markov.chat(msg.content.split(" ", 1)[1], msg.author.guild.id, True))

    @commands.command(no_pm=True, pass_context=True)
    async def replyrate(self, ctx):
        msg = ctx.message
        async with msg.channel.typing():
            return await msg.channel.send(self.markov.change_replyrate(msg, msg.author.id, msg.channel.id))


def setup(bot):
    bot.add_cog(Markov(bot))
