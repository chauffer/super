import aiohttp
import traceback

import structlog


logger = structlog.getLogger(__name__)


class Gif:

    def __init__(self):
        self.api = "https://rightgif.com/search/web"
        self.session = aiohttp.ClientSession()
        self.help = "**.gif** <query> - random gif"

    async def url_valid(self, url):
        try:
            async with self.session.get(url, timeout=1) as resp:
                if resp.status < 400:
                    return True
        except:
            logger.error(
                "utils/gif/url_valid: Error", error=traceback.print_exc(), url=url
            )
        return False

    async def get_url(self, text):
        logger.debug("utils/gif/get_url: Searching", query=text)
        async with self.session.post(
            "https://rightgif.com/search/web", data={"text": text}, timeout=5,
        ) as resp:
            data = await resp.json()
            logger.info("utils/gif/get_url: Fetched", url=data["url"])
            return data["url"]

    async def chat(self, msg):
        message = msg.split()
        if len(message < 2):
            return self.help
        url = await self.get_url(message[1])
        if self.url_valid(url):
            return url
        else:
            return "no result"
