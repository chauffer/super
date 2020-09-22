from aiocache import Cache, cached
from super.utils import R


url = "https://en.wikipedia.org/w/api.php"

@cached(cache=Cache.REDIS, ttl=3600, endpoint=R.host, port=R.port)
async def get_url(session, title):
    async with session.get(
        url,
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
async def wiki(session, query, offset=0):
    async with session.get(
        url,
        params={
            "action": "query",
            "list": "search",
            "format": "json",
            "srsearch": query,
            "sroffset": offset,
        },
    ) as response:
        return (await response.json())["query"]["search"]
