import os
import time
import traceback

import aiohttp
import ics
from ago import human
from arrow import Arrow

from discord.ext import commands
from super import utils


class F1:
    def __init__(self, bot):
        self.bot = bot
        self.calendar = None

    async def _get_calendar(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                'https://www.f1calendar.com/download/f1-calendar_p1_p2_p3_q_gp.ics',
                params={'t': int(time.time())},
                timeout=5,
            ) as resp:
                data = await resp.text()
        return ics.Calendar(data)

    async def get_events(self, num, ongoing=True):
        if not self.calendar:
            self.calendar = await self._get_calendar()

        now = Arrow.now()
        lines, lines_on = [], []
        for event in self.calendar.events[::-1]:
            if event.end < now:
                continue
            if event.end > now > event.begin and ongoing:
                lines_on.append(f'**{event.name}** ongoing')
            else:
                lines.append('**{0}** {1}, {2}'.format(
                    event.name,
                    human(event.begin.timestamp, precision=2),
                    event.begin.strftime('%d %b @ %H:%M'),
                ))
            if len(lines) >= num:
                break
        return lines_on + lines

    @commands.command(no_pm=True, pass_context=True)
    async def f1ns(self, ctx):
        """Formula 1 next session"""
        utils.send_typing(self, ctx.message.channel)
        await self.bot.say('\n'.join(await self.get_events(1)))

    @commands.command(no_pm=True, pass_context=True)
    async def f1ls(self, ctx):
        """Formula 1 list sessions"""
        utils.send_typing(self, ctx.message.channel)
        await self.bot.say('\n'.join(await self.get_events(10)))


def setup(bot):
    bot.add_cog(F1(bot))
