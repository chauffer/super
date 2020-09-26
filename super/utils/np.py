from asyncio import gather
import json
import aiohttp

from super import settings
from super.utils import R


class Np:
    def __init__(self):
        self.url = "https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks"
        self.session = aiohttp.ClientSession()

    def __exit__(self):
        self.session.close()

    def lastfm_response_to_song(self, response):
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

    def lastfm_song_to_str(self, lfm, nick, song):
        nick = f"({nick})" if nick else ""
        return " ".join(
            [
                f"**{lfm}**{nick}",
                f"now playing: **{song['artist']} - {song['name']}**",
                f"from **{song['album']}**" if song["album"] else "",
            ]
        )

    async def userid_to_lastfm(self, ctx, member):
        lfm = await R.read(R.get_slug(ctx, "np", id=member.id))
        return [lfm, member.display_name]

    async def lastfm(self, lfm=None, ctx=None, member=None, nick=None):
        if not lfm:
            lfm, nick = await self.userid_to_lastfm(ctx, member)
        if not lfm:
            return

        params = dict(
            format="json", limit=1, user=lfm, api_key=settings.SUPER_LASTFM_API_KEY
        )

        async with self.session.get(self.url, params=params) as response:
            response = json.loads(await response.read())
        song = self.lastfm_response_to_song(response)
        return {
            "song": song,
            "formatted": self.lastfm_song_to_str(lfm, nick, song),
        }

    async def np(self, ctx):
        async with ctx.message.channel.typing():
            words = ctx.message.content.split(" ")
            slug = R.get_slug(ctx, "np")
            try:
                lfm = words[1]
                await R.write(slug, lfm)
            except IndexError:
                lfm = await R.read(slug)

            if not lfm:
                return await ctx.message.channel.send(
                    f"Set an username first, e.g.: **{settings.SUPER_PREFIX}np joe**"
                )
            return await ctx.message.channel.send(
                (await self.lastfm(lfm=lfm))["formatted"]
            )

    async def wp(self, ctx):
        async with ctx.message.channel.typing():
            message = ["Users playing music in this server:"]
            tasks = []
            for member in ctx.message.guild.members:
                tasks.append(self.lastfm(ctx=ctx, member=member))

            tasks = tasks[::-1]  ## Theory: this will make it ordered by join date

            for data in await gather(*tasks):
                if data and data["song"]["is_playing"]:
                    message.append(data["formatted"])
            if len(message) == 1:
                message.append("Nobody. :disappointed:")
            return await ctx.message.channel.send("\n".join(message))
