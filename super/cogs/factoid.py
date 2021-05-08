import json

from aiocache import Cache, cached
from discord.ext import commands
from super import settings
from super.utils import R


class RegexReply(commands.Cog):
    """RegexReply"""

    def __init__(self, bot):
        self.bot = bot
        self.regexes = {}

    def __exit__(self):
        ...

    async def _get_regexes(self, ctx):
        r = await R.read(R.get_slug(ctx, "regexreply"))
        return json.loads(r) if r else {}

    async def _put_regexes(self, ctx, data):
        return await R.write(R.get_slug(ctx, "regexreply"), json.dumps(data))

    async def pull(self, ctx):
        regexes = await self._get_regexes(ctx)
        self.regexes[ctx.message.author.guild.id] = regexes

    async def push(self, ctx):
        data = self.regexes[ctx.message.author.guild.id]
        self._put_regexes(ctx, data)

    @commands.command(no_pm=True, pass_context=True)
    async def np(self, ctx):
        """**.np** - Now playing song from last.fm"""
        async with ctx.message.channel.typing():
            words = ctx.message.content.split(" ")
            slug = R.get_slug(ctx, "np")
            try:
                lfm = words[1]
                await R.write(slug, lfm)
            except IndexError:
                lfm = await R.read(slug)

            if not lfm:
                await ctx.message.channel.send(
                    f"Set an username first, e.g.: **{settings.SUPER_PREFIX}np joe**"
                )
                return
            lastfm_data = await self.lastfm(lfm=lfm)
            return await ctx.message.channel.send(lastfm_data["formatted"])

    @commands.command(no_pm=True, pass_context=True, name="wp")
    async def wp(self, ctx):
        """**.wp** - Now playing, for the whole server"""
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


def setup(bot):
    bot.add_cog(Np(bot))
