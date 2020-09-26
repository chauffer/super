from contextlib import suppress
import os
import random
import re
from cobe.brain import Brain
from super import settings
from super.utils import R, owoify


class Markov:
    def get_brain(self, server):
        return Brain(f"/data/cobe/{server}")

    def get_slug(self, channel):
        return R.slug_to_str(["markov_replyrate", channel])

    async def get_replyrate(self, channel):
        slug = self.get_slug(channel)

        replyrate = await R.read(slug)
        if not replyrate:
            return 0
        return int(replyrate)

    async def should_reply(self, channel):
        return random.randint(0, 100) < await self.get_replyrate(channel)

    def sanitize_out(self, msg):
        replacements = {
            "@here": "**@**here",
            "@everyone": "**@**everyone",
        }
        for key, val in replacements.items():
            message = message.replace(key, val)
        return message

    async def chat(self, ctx, owo=False):
        async with ctx.message.channel.typing():
            brain = self.get_brain(ctx.message.author.guild.id)
            if owo:
                return await ctx.message.channel.send(
                    owoify(brain.reply(ctx.message.content.split(" ", 1)[1]))
                )
            return await ctx.message.channel.send(
                brain.reply(ctx.message.content.split(" ", 1)[1])
            )

    async def replyrate(self, ctx):
        # if str(ctx.message.author.id) not in settings.SUPER_ADMINS:
        #     return await ctx.message.channel.send("no")

        message = ctx.message.content.split(" ")
        try:
            replyrate = int(message[1])
            if not 0 <= replyrate <= 100:
                return await ctx.message.channel.send("0-100")
        except IndexError:
            return await ctx.message.channel.send("0-100")

        await R.write(self.get_slug(ctx.message.channel.id), replyrate)
        return await ctx.message.channel.send(f"Reply rate set to {replyrate}%")

    async def reply(self, message, bot_id):
        if message.author.bot:  # Ignore bots
            return
        if message.content.startswith(settings.SUPER_PREFIX):  # Ignore commands
            return

        brain = self.get_brain(message.author.guild.id)

        mention = r"<@!?" + str(bot_id) + ">"

        mentioned = any(bot_id == m.id for m in message.mentions)

        learned_message = re.sub(mention, "Super", message.content).strip()
        learned_message = re.sub("^Super ", "", learned_message)
        brain.learn(learned_message)

        if mentioned or await self.should_reply(message.channel.id):
            reply = self.sanitize_out(brain.reply(learned_message))
            if reply == message.content:
                return

            return await message.channel.send(reply)
