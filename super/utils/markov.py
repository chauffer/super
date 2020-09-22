import os
import random
from cobe.brain import Brain
from super.utils import R, owoify


def get_brain(server):
    return Brain(f"/data/cobe/{server}")

def get_slug(channel):
    return R.slug_to_str(["markov_replyrate", channel])

async def get_replyrate(channel):
    slug = get_slug(channel)

    replyrate = await R.read(slug)
    if not replyrate:
        return 0
    return int(replyrate)

async def should_reply(channel):
    return random.randint(0, 100) < await get_replyrate(channel)

def sanitize_out(message):
    replacements = {
        "@here": "**@**here",
        "@everyone": "**@**everyone",
    }
    for key, val in replacements.items():
        message = message.replace(key, val)
    return message
