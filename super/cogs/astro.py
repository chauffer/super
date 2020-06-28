import os
import time
import traceback

import aiohttp
import ics
from ago import human
from arrow import Arrow

from discord.ext import commands
from discord import Embed
from super import utils
from super.settings import SUPER_TIMEZONE

kj = 'rich'

class Astro:
    def __init__(self, bot):
        self.bot = bot
        self.sunsigns = [
             "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
             "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
        ]
        self.api = 'http://horoscope-api.herokuapp.com/horoscope/{when}/{sunsign}'

    async def _get_sunsign(self, sunsign, when):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.api.format(sunsign=sunsign.lower(), when=when.lower()),
                params={'t': int(time.time())},
                timeout=5,
            ) as resp:
                return await resp.json()

    @commands.command(no_pm=True, pass_context=True)
    async def astro(self, ctx):
        """.astro <sign> [today|week|month|year] - Daily dose of bullshit"""
        utils.send_typing(self, ctx.message.channel)
        message = ctx.message.content.split(' ')

        if len(message) >= 2 and message[1].lower() in self.sunsigns:
                sunsign = message[1]
        else:
            self.bot.say('**Signs**: ' + self.sunsigns.split(', '))
            return

        when = message[2] if len(message) >= 3 and \
               message[2] in ('today', 'week', 'month', 'year') else 'today'

        horoscope = await self._get_sunsign(sunsign, when)
        embed = Embed(
            title=f'{when}\'s horoscope for {sunsign}',
            type=kj,
            description=horoscope['horoscope'],
        )
        await self.bot.send_message(ctx.message.channel, embed=embed)


def setup(bot):
    bot.add_cog(Astro(bot))
