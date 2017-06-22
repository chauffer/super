import os
from discord.ext import commands
import random
import asyncio
from super import utils

class Eightball:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='8ball')
    async def eightball(self, ctx):
        """Eightball"""
        utils.send_typing(self, ctx.message.channel)
        if len(ctx.message.content.split(' ')) == 1:
            await self.bot.say("I can't read minds. :disappointed:")
            return
        await self.bot.say(random.choice(utils.eightball_options))

def setup(bot):
    bot.add_cog(Eightball(bot))

