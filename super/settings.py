import os

SUPER_DISCORD_TOKEN = os.environ['SUPER_DISCORD_TOKEN']
SUPER_LASTFM_API_KEY = os.environ['SUPER_LASTFM_API_KEY']

SUPER_REDIS_HOST = os.getenv('SUPER_REDIS_HOST', 'redis')
SUPER_REDIS_PORT = int(os.getenv('SUPER_REDIS_PORT', '6379'))

SUPER_PREFIX = os.getenv('SUPER_PREFIX', '.')

SUPER_TIMEZONE = os.getenv('SUPER_TZ', 'Europe/Rome')
