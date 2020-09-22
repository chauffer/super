import traceback

import structlog


logger = structlog.getLogger(__name__)

async def url_valid(session, url):
    try:
        async with session.get(url, timeout=1) as resp:
            if resp.status < 400:
                return True
    except:
        logger.error(
            "utils/gif/url_valid: Error", error=traceback.print_exc(), url=url
        )
    return False

async def get_url(session, text):
    logger.debug("utils/gif/get_url: Searching", query=text)
    async with session.post(
        "https://rightgif.com/search/web", data={"text": text}, timeout=5,
    ) as resp:
        data = await resp.json()
        logger.info("utils/gif/get_url: Fetched", url=data["url"])
        return data["url"]
