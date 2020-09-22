import aioredis
import asyncio
from contextlib import asynccontextmanager
import pytest
from .utils.fuzzy import fuz
from .utils.redis import SuperRedis
from unittest import mock


class TestFuzzy:
    """Tests for fuzzywuzzy."""

    def test_fuzzy_match(self):
        """Test correct fuzzy match."""
        words = ['start', 'stop', 'resume', 'pause']
        assert 'start' == fuz('ster', words)

    def test_fuzzy_default(self):
        """Test default return from fuzzy."""
        words = ['start', 'stop']
        assert 'leave' == fuz('leave', words, 'leave')

    def test_fuzzy_no_match(self):
        """Test if no match returns None from fuzzy."""
        words = ['start', 'stop']
        assert None == fuz('leave', words)


class TestRedis:
    """Tests for Redis."""

    @pytest.fixture
    async def redis(self):
        R = SuperRedis('redis')
        yield R

    @pytest.mark.asyncio
    async def test_redis_read(self, redis):
        """Test if values can be read from redis."""
        assert None == await redis.read('test')

    @pytest.mark.asyncio
    async def test_redis_write(self, redis):
        """Test if values can be written to redis."""
        await redis.write('test', 'test')
        assert 'test' == await redis.read('test')

    @pytest.mark.asyncio
    async def test_redis_lock(self, redis):
        """Test if lock expires after duration."""
        await redis.lock('lock_test', 0.001)
        await asyncio.sleep(1)
        assert None == await redis.read('lock_test')

    @pytest.mark.asyncio
    async def test_redis_slug(self, redis):
        """Test if redis returns right slug."""
        assert redis.slug_to_str(['test']) == 'super:test'
