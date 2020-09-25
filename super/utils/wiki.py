from aiocache import Cache, cached
import aiohttp
from super.utils import R
import structlog

logger = structlog.getLogger(__name__)


class Wiki:
    def __init__(self):
        self.url = "https://en.wikipedia.org/w/api.php"
        self.session = aiohttp.ClientSession()

    @cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
    async def get_url(self, title):
        async with self.session.get(
            self.url,
            params={
                "action": "query",
                "prop": "info",
                "format": "json",
                "generator": "allpages",
                "inprop": "url",
                "gapfrom": title,
                "gaplimit": 1,
            },
        ) as r:
            return list((await r.json())["query"]["pages"].items())[0][1]["fullurl"]

    @cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
    async def wiki(self, query, offset=0):
        async with self.session.get(
            self.url,
            params={
                "action": "query",
                "list": "search",
                "format": "json",
                "srsearch": query,
                "sroffset": offset,
            },
        ) as response:
            return (await response.json())["query"]["search"]

    async def search(self, query, index):
        logger.debug("utils/wiki/search: Fetching", query=query, index=index)
        try:
            result = (await self.wiki(query, 10 * (index // 10)))[index % 10]
        except IndexError:
            return "?"

        return await (await self.get_url(result["title"]))