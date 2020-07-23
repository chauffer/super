import aiohttp
import ics
from ago import human
from arrow import Arrow
from discord.ext import commands
from super.settings import SUPER_TIMEZONE, SUPER_F1_CALENDAR
from contextlib import suppress


class F1(commands.Cog):
    """Formula 1"""

    def __init__(self, bot):
        self.bot = bot
        self._calendar = None

    async def calendar(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(SUPER_F1_CALENDAR, timeout=5) as resp:
                    self._calendar = ics.Calendar(await resp.text())
                    return self._calendar
        except:
            return self._calendar

    async def get_events(self, num, page=0, more=False):
        lines = []
        calendar = await self.calendar()
        start = min(page * num, len(calendar.events) - num)
        for event in sorted(calendar.events, key=lambda x: x.begin)[start:]:
            if event.end > Arrow.now() > event.begin:
                lines.append(f"**{event.name}** ongoing")
            elif event.begin > Arrow.now():
                local_time = event.begin.to(SUPER_TIMEZONE)
                lines.append(
                    "**{0}** {1}, {2}".format(
                        event.name,
                        human(local_time.timestamp, precision=2),
                        local_time.strftime("%d %b @ %H:%M"),
                    )
                )
            if len(lines) >= num:
                break
        if more and len(calendar.events) - start - num:
            lines.append(f"...and {len(calendar.events) - start - num} more")
        return lines

    @commands.command(no_pm=True, pass_context=True)
    async def f1ns(self, ctx):
        """**.f1ns** - Formula 1 next session"""
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send("\n".join(await self.get_events(1)))

    @commands.command(no_pm=True, pass_context=True)
    async def f1ls(self, ctx):
        """**.f1ls** [page] - Formula 1 list sessions"""
        page = 1
        if len(ctx.message.content.split()[1:]):
            with suppress(Exception):
                page = int(ctx.message.content.split()[1])

        events = "\n".join(await self.get_events(10, page, more=True))
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(events)


def setup(bot):
    bot.add_cog(F1(bot))
