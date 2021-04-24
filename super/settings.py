import os

SUPER_DISCORD_TOKEN = os.environ["SUPER_DISCORD_TOKEN"]
SUPER_LASTFM_API_KEY = os.environ["SUPER_LASTFM_API_KEY"]

SUPER_REDIS_HOST = os.getenv("SUPER_REDIS_HOST", "redis")
SUPER_REDIS_PORT = int(os.getenv("SUPER_REDIS_PORT", "6379"))

SUPER_PREFIX = os.getenv("SUPER_PREFIX", ".")

SUPER_TIMEZONE = os.getenv("SUPER_TZ", "Europe/Rome")
SUPER_ADMINS = os.getenv("SUPER_ADMINS", "").split(",")

SUPER_F1_CALENDAR = os.getenv(
    "SUPER_F1_CALENDAR",
    "https://f1calendar.com/download/f1-calendar_p1_p2_p3_q_gp.ics",
)

SUPER_HELP_COLOR = int(os.getenv("SUPER_BOT_COLOR", "#c53a91").strip("#"), 16)

SUPER_QUEUE_PAGINATION = int(os.getenv("SUPER_QUEUE_PAGINATION", 10))

SUPER_YOUTUBE_API_KEY = os.environ["SUPER_YOUTUBE_API_KEY"]

SUPER_MAX_YOUTUBE_LENGTH = int(os.getenv("SUPER_MAX_YOUTUBE_LENGTH", 6 * 60 * 60))

SUPER_YOUTUBE_TIMEOUT = int(os.getenv('SUPER_YOUTUBE_TIMEOUT', 600))

SUPER_DEBUG = os.getenv("SUPER_DEBUG") is not None
