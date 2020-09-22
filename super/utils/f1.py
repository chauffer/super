import aiohttp
import ics
from ago import human
from arrow import Arrow
import structlog
from super.settings import SUPER_TIMEZONE, SUPER_F1_CALENDAR
from contextlib import suppress

logger = structlog.getLogger(__name__)

_calendar = None

async def get_calendar():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SUPER_F1_CALENDAR, timeout=5) as resp:
                return ics.Calendar(await resp.text())
    except:
        return _calendar

async def get_events(num=10, page=0, more=False, weekend=False):
    logger.debug(
        "utils/f1/get_events: Fetching", num=num, more=more, weekend=weekend
    )
    lines = []
    calendar = await get_calendar()
    start = min(page * num, len(calendar.events) - num)
    for event in sorted(calendar.events, key=lambda x: x.begin)[start:]:
        if event.end > Arrow.now() > event.begin:
            event_end = human(event.end.to(SUPER_TIMEZONE).timestamp, precision=2)
            lines.append(f"**{event.name}** ongoing, ending in {event_end}")
        elif event.begin > Arrow.now():
            local_time = event.begin.to(SUPER_TIMEZONE)
            lines.append(
                "**{0}** {1}, {2}".format(
                    event.name,
                    human(local_time.timestamp, precision=2),
                    local_time.strftime("%d %b @ %H:%M"),
                )
            )
            if weekend and local_time.isoweekday() in (7, 1):
                break
        if len(lines) >= num:
            break
    if more and len(calendar.events) - start - num:
        lines.append(f"...and {len(calendar.events) - start - num} more")
    logger.info("utils/f1/get_events: Fetched", result=lines)
    return lines
