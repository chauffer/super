import os
from discord.ext import commands
import time
import asyncio

class Ping:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """Shows how long it takes for the bot to send & edit a message"""
        before = time.time()
        m = await self.bot.send_message(ctx.message.channel, '1/3 .')
        await self.bot.edit_message(m, '2/3 ..')
        benchmark = int((time.time() - before) * 1000)
        await self.bot.edit_message(m, f'3/3 ... {benchmark}ms')

def setup(bot):
    bot.add_cog(Ping(bot))
