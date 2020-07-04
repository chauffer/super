import os
import random
import re
from discord.ext import commands
from cobe.brain import Brain
from super import settings
from super.utils import R


class Markov(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs("/data/cobe/", exist_ok=True)

    def _get_brain(self, server):
        return Brain(f"/data/cobe/{server}")

    def _get_slug(self, channel):
        return R.slug_to_str(["markov_replyrate", channel])

    async def _get_replyrate(self, channel):
        slug = self._get_slug(channel)

        replyrate = await R.read(slug)
        if not replyrate:
            return 0
        return int(replyrate)

    async def should_reply(self, channel):
        return random.randint(0, 100) < await self._get_replyrate(channel)

    def sanitize_out(self, message):
        replacements = {
            "@here": "**@**here",
            "@everyone": "**@**everyone",
        }
        for key, val in replacements.items():
            message = message.replace(key, val)
        return message

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # Ignore bots
            return
        if message.content.startswith(settings.SUPER_PREFIX):  # Ignore commands
            return
        brain = self._get_brain(message.author.guild.id)

        mention = r"<@!?" + str(self.bot.user.id) + ">"

        mentioned = any(self.bot.user.id == m.id for m in message.mentions)

        learned_message = re.sub(mention, "Super", message.content).strip()
        brain.learn(learned_message)

        if mentioned or await self.should_reply(message.channel.id):
            reply = self.sanitize_out(brain.reply(message.content))
            return await message.channel.send(reply)

    @commands.command(no_pm=True, pass_context=True)
    async def chat(self, ctx):
        """.chat <text> - Reply to a message"""
        async with ctx.message.channel.typing():
            brain = self._get_brain(ctx.message.author.guild.id)
            about = ctx.message.content.split(" ", 1)[1]
            return await ctx.message.channel.send(brain.reply(about))

    @commands.command(no_pm=True, pass_context=True)
    async def replyrate(self, ctx):
        if ctx.message.author.id not in settings.SUPER_ADMINS:
            return await ctx.message.channel.send(f"You cannot configure this.")
        message = ctx.message.content.split(" ")
        replyrate = int(message[1])

        if not 0 <= replyrate <= 100:
            return await ctx.message.channel.send("0-100")

        await R.write(self._get_slug(ctx.message.channel.id), replyrate)
        return await ctx.message.channel.send(f"Reply rate set to {replyrate}%")


def setup(bot):
    bot.add_cog(Markov(bot))
