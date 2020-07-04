# Super - Yet Another Yet Another Python Discord Bot

Super is a discord bot containing support commands for:

* Translations
* Connection diagnostics
* Last.fm integration
* Markov chain
* Gif search
* Eightball generator
* Formula 1 Schedule
* Horoscopes

## Installation

1. Clone the repository
2. [Create Discord App](https://discordpy.readthedocs.io/en/latest/discord.html)
3. Copy the app token and set .env file
4. `docker-compose up`

Environment variables:


|        Name            |                    Description                  | Required |   Default   |
|------------------------|-------------------------------------------------|----------|-------------|
| `SUPER_DISCORD_TOKEN`  | Discord application token                       |   Yes    |             |
| `SUPER_LASTFM_API_KEY` | Last.fm API token                               |   Yes    |             |
| `SUPER_REDIS_HOST`     | Redis host, if left empty, will use local redis |   No     | redis       |
| `SUPER_REDIST_PORT`    | Redis port, if left empty, will use local redis |   No     | 6379        |
| `SUPER_PREFIX`         | Prefix of bot commands                          |   No     | .           |
| `SUPER_TIMEZONE`       | Timezone of the bot                             |   No     | Europe/Rome |
| `SUPER_ADMINS`         | Users with full access to bot commands          |   No     |             |
| `SUPER_F1_CALENDAR`    | URL for F1 Schedule                             |   No     | [Official Calendar](https://calendar.google.com/calendar/ical/ekqk1nbdusr1baon1ic42oeeik%40group.calendar.google.com/public/basic.ics) |
| `SUPER_HELP_COLOR`     | Color of help command (in #ffffff format)                  |   No     | #c53a91    |


## Cogs

To install cogs in `run.py` append new cog location to `extensions` list.
All cogs must have docstrings describing the cog class and docstring on each command function describing command usage.
