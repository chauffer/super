import asyncio

import aioredis
import structlog

from . import settings

conn = None
logger = structlog.getLogger(__name__)


class SuperRedis:
    def __init__(self, host=None, port=6379):
        logger.debug("utils/superredis/connect: connecting...", host=host, port=port)
        self.host, self.port = host, port
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())

    async def connect(self):
        self.pool = await aioredis.create_pool(
            (self.host, self.port), minsize=50, maxsize=100,
        )
        logger.info(
            "utils/superredis/connect: connected!", host=self.host, port=self.port
        )

    async def write(self, slug, value):
        slug = self.slug_to_str(slug)
        with await self.pool as redis:
            return await redis.execute("set", slug, value)

    async def read(self, slug):
        slug = self.slug_to_str(slug)
        with await self.pool as redis:
            return await redis.execute("get", slug, encoding="utf-8")

    async def lock(self, slug, time=600):
        slug = self.slug_to_str(slug)
        with await self.pool as redis:
            locked = bool(await redis.execute("setnx", slug, 1))
            if locked:
                await redis.execute("expire", slug, time * 1000)
        return locked

    def get_slug(self, ctx, command=None, id=None):
        slug = [
            ctx.message.author.guild.id,
            id or ctx.message.author.id,
        ]
        if command:
            slug.append(command)
        return self.slug_to_str(slug)

    @staticmethod
    def slug_to_str(slug):
        if type(slug) == list:
            slug = ":".join([str(o) for o in slug])
        return "super:" + slug
