from .. import settings
from .eightball import eightball_options
from .funny_text import owoify
from .fuzzy import fuz
from .redis import SuperRedis

R = SuperRedis(host=settings.SUPER_REDIS_HOST, port=settings.SUPER_REDIS_PORT,)
