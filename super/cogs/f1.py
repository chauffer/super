import time
import aiohttp
import ics
from ago import human
from arrow import Arrow
from discord.ext import commands
from super.settings import SUPER_TIMEZONE, SUPER_F1_CALENDAR


class F1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.calendar = None

    async def _get_calendar(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    SUPER_F1_CALENDAR,
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
        for event in self.calendar.events:
            if event.end < now:
                continue
            if event.end > now > event.begin and ongoing:
                lines_on.append(f'**{event.name}** ongoing')
            else:
                local_time = event.begin.to(SUPER_TIMEZONE)
                lines.append('**{0}** {1}, {2}'.format(
                    event.name,
                    human(local_time.timestamp, precision=2),
                    local_time.strftime('%d %b @ %H:%M'),
                ))
            if len(lines) >= num:
                break
        return lines_on + lines

    @commands.command(no_pm=True, pass_context=True)
    async def f1ns(self, ctx):
        """Formula 1 next session"""
        async with ctx.message.channel.typing():
            events = '\n'.join(await self.get_events(1))
            return await ctx.message.channel.send(events)

    @commands.command(no_pm=True, pass_context=True)
    async def f1ls(self, ctx):
        """Formula 1 list sessions"""
        async with ctx.message.channel.typing():
            events = '\n'.join(await self.get_events(10))
            return await ctx.message.channel.send(events)


def setup(bot):
    bot.add_cog(F1(bot))
