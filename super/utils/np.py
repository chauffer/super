from asyncio import gather
import json
import aiohttp

from super import settings
from super.utils import R


def lastfm_response_to_song(response):
    song = dict(is_playing=False)
    try:
        track = response["recenttracks"]["track"][0]
        song["artist"] = track["artist"]["#text"]
        song["album"] = track["album"]["#text"] or None
        song["name"] = track["name"]

        if "@attr" in track and "nowplaying" in track["@attr"]:
            song["is_playing"] = True
    except (KeyError, IndexError):
        song = dict(is_playing=True, artist=None, album=None, name=None)
    return song

def lastfm_song_to_str(lfm, nick, song):
    nick = f"({nick})" if nick else ""
    return " ".join(
        [
            f"**{lfm}**{nick}",
            f"now playing: **{song['artist']} - {song['name']}**",
            f"from **{song['album']}**" if song["album"] else "",
        ]
    )

async def userid_to_lastfm(ctx, member):
    lfm = await R.read(R.get_slug(ctx, "np", id=member.id))
    return [lfm, member.display_name]

async def lastfm(session, lfm=None, ctx=None, member=None, nick=None):
    if not lfm:
        lfm, nick = await userid_to_lastfm(ctx, member)
    if not lfm:
        return

    url = "https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks"
    params = dict(
        format="json", limit=1, user=lfm, api_key=settings.SUPER_LASTFM_API_KEY
    )

    async with session.get(url, params=params) as response:
        response = json.loads(await response.read())
    song = lastfm_response_to_song(response)
    return {
        "song": song,
        "formatted": lastfm_song_to_str(lfm, nick, song),
    }
