import os
from discord.ext import commands
from cobe.brain import Brain
from super import settings, utils
import asyncio

class markov:
    def __init__(self, bot):
        self.bot = bot
        os.makedirs('/data/cobe/', exist_ok=True)


    def _get_brain(self, server):
        return Brain(f'/data/cobe/{server}')


    async def on_message(self, message):
        if message.author.bot:  # Ignore bots
            return
        if message.content.startswith(settings.SUPER_PREFIX): # Ignore commands
            return
        brain = self._get_brain(message.author.server.id)
        brain.learn(message.content)


    @commands.command(no_pm=True, pass_context=True)
    async def chat(self, ctx):
        utils.send_typing(self, ctx.message.channel)
        brain = self._get_brain(ctx.message.author.server.id)
        about = ctx.message.content.split(' ', 1)[1]
        await self.bot.say(brain.reply(about))


def setup(bot):
    bot.add_cog(markov(bot))
