from contextlib import suppress

import aiohttp
import ics
from ago import human
from arrow import Arrow

import structlog
from discord.ext import commands
from super.settings import SUPER_F1_CALENDAR, SUPER_TIMEZONE
from super.utils import R

logger = structlog.getLogger(__name__)


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

    async def get_events(self, num=10, page=0, more=False, weekend=False):
        logger.debug(
            "cogs/f1/get_events: Fetching", num=num, more=more, weekend=weekend
        )
        lines = []
        calendar = await self.calendar()
        timeline = list(calendar.timeline.start_after(Arrow.now()))
        start = min(page * num, len(timeline) - num)
        
        logger.info("cogs/f1/get_events", start=start, len_timeline=len(timeline))

        for event in list(calendar.timeline.now()):
            lines.append(
                f"**{event.name}** ongoing, ending " +
                human(event.end.to(SUPER_TIMEZONE).timestamp, precision=2)
            )

        for event in list(timeline)[start:]:
                local_time = event.begin.to(SUPER_TIMEZONE)
                lines.append(
                    "**{0}** {1}, {2}".format(
                        event.name,
                        human(local_time.timestamp, precision=2),
                        local_time.strftime("%d %b @ %H:%M"),
                    )
                )
                if len(lines) >= num or weekend and local_time.isoweekday() in (7, 1):
                    break
        if more and len(timeline) - start - num:
            lines.append(f"...and {len(timeline) - start - num} more")
        logger.info("cogs/f1/get_events: Fetched", result=lines)
        return lines

    @commands.command(pass_context=True)
    async def f1(self, ctx):
        """**.f1** - Formula 1 sessions this weekend"""
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(
                "\n".join(await self.get_events(weekend=True))
            )

    @commands.command(pass_context=True)
    async def f1ns(self, ctx):
        """**.f1ns** - Formula 1 next session"""
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send("\n".join(await self.get_events(1)))

    @commands.command(pass_context=True)
    async def f1ls(self, ctx):
        """**.f1ls** [page] - Formula 1 list sessions"""
        page = 1
        if len(ctx.message.content.split()[1:]):
            with suppress(Exception):
                page = int(ctx.message.content.split()[1])

        events = "\n".join(await self.get_events(page=page-1, more=True))
        async with ctx.message.channel.typing():
            return await ctx.message.channel.send(events)


def setup(bot):
    bot.add_cog(F1(bot))
