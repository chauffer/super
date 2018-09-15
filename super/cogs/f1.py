import os
import time
import traceback

import aiohttp
import arrow
import ics

from discord.ext import commands
from super import utils


class F1:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.calendar = None

    def __exit__(self):
        self.session.close()

    async def _get_calendar(self):
        async with self.session.get(
            'https://www.f1calendar.com/download/f1-calendar_p1_p2_p3_q_gp.ics',
            params={'t': int(time.time())},
            timeout=5,
        ) as resp:
            data = await resp.text()
        return ics.Calendar(data)

    @commands.command(no_pm=True, pass_context=True)
    async def f1ns(self, ctx):
        """.f1ns - Formula 1 next session."""
        utils.send_typing(self, ctx.message.channel)

        if not self.calendar:
            self.calendar = await self._get_calendar()

        now = arrow.Arrow.now()
        lines = []
        for event in self.calendar.events[::-1]:
            if event.end < now:
                continue
            if event.end > now > event.begin:
                lines.append(f'**{event.name}** ongoing')
            else:
                lines.append(f'**{event.name}** {event.begin.humanize()}')
                break
        await self.bot.say('\n'.join(lines))

def setup(bot):
    bot.add_cog(F1(bot))
