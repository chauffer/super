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
        os.makedirs("/data/cobe/", exist_ok=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # Ignore bots
            return
        if message.content.startswith(settings.SUPER_PREFIX):  # Ignore commands
            return
        brain = markov.get_brain(message.author.guild.id)

        mention = r"<@!?" + str(self.bot.user.id) + ">"

        mentioned = any(self.bot.user.id == m.id for m in message.mentions)

        learned_message = re.sub(mention, "Super", message.content).strip()
        learned_message = re.sub("^Super ", "", learned_message)
        brain.learn(learned_message)

        if mentioned or await markov.should_reply(message.channel.id):
            reply = markov.sanitize_out(brain.reply(learned_message))
            if reply == message.content:
                return

            return await message.channel.send(reply)

    @commands.command(no_pm=True, pass_context=True)
    async def chat(self, ctx):
        """**.chat** <text> - Reply to a message"""
        async with ctx.message.channel.typing():
            brain = markov.get_brain(ctx.message.author.guild.id)
            about = ctx.message.content.split(" ", 1)[1]
            return await ctx.message.channel.send(brain.reply(about))

    @commands.command(no_pm=True, pass_context=True)
    async def owochat(self, ctx):
        """**.owochat** <text> - Reply to a message, owoified"""
        async with ctx.message.channel.typing():
            brain = markov.get_brain(ctx.message.author.guild.id)
            about = ctx.message.content.split(" ", 1)[1]
            return await ctx.message.channel.send(owoify(brain.reply(about)))

    @commands.command(no_pm=True, pass_context=True)
    async def replyrate(self, ctx):
        if str(ctx.message.author.id) not in settings.SUPER_ADMINS:
            return await ctx.message.channel.send(f"no")

        message = ctx.message.content.split(" ")
        replyrate = int(message[1])

        if not 0 <= replyrate <= 100:
            return await ctx.message.channel.send("0-100")

        await R.write(markov.get_slug(ctx.message.channel.id), replyrate)
        return await ctx.message.channel.send(f"Reply rate set to {replyrate}%")


def setup(bot):
    bot.add_cog(Markov(bot))
