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

    async def chat(self, msg, guild, owo=False):
        brain = self.get_brain(guild)
        if owo:
            return owoify(brain.reply(msg))
        return brain.reply(msg)

    async def change_replyrate(self, msg, author_id, channel_id):
        if str(author_id) not in settings.SUPER_ADMINS:
            return "no"

        message = msg.content.split(" ")
        replyrate = int(message[1])
        if not 0 <= replyrate <= 100:
            return "0-100"

        await R.write(self.get_slug(channel_id), replyrate)
        return f"Reply rate set to {replyrate}%"

    async def reply(self, msg, bot_id, guild_id, channel_id, mentions):
        brain = self.get_brain(guild_id)

        mention = r"<@!?" + str(bot_id) + ">"

        mentioned = any(bot_id == m.id for m in mentions)

        learned_message = re.sub(mention, "Super", msg).strip()
        learned_message = re.sub("^Super ", "", learned_message)
        brain.learn(learned_message)

        if mentioned or await self.should_reply(channel_id):
            reply = self.sanitize_out(brain.reply(learned_message))
            if reply == msg:
                return

            return reply