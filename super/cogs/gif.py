import os
from discord.ext import commands
from super import utils
import aiohttp
import traceback

class Gif:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __exit__(self):
        self.session.close()


    async def _url_valid(self, url):
        try:
            async with self.session.get(url, timeout=1) as resp:
                if resp.status < 400:
                    return True
        except:
            traceback.print_exc()
        return False

    async def _get_url(self, text, nsfw):
        async with self.session.get(
            'https://api.gifme.io/v1/search',
            data=dict(key='rX7kbMzkGu7WJwvG', query=text, nsfw=nsfw),
            timeout=5,
        ) as resp:
            data = await resp.json()
        for image in data['data']:
            if await self._url_valid(image['link']):
                return image['link']

            async with self.session.post(
                'https://rightgif.com/search/web',
                data={'text': text},
                timeout=5,
            ) as resp:
                data = await resp.json()
                return data['url']

    @commands.command(no_pm=True, pass_context=True)
    async def gif(self, ctx):
        """.gif [nsfw] query - Gives you a random gif."""
        utils.send_typing(self, ctx.message.channel)
        text = ctx.message.content.split(' ', 1)[1]
        nsfw = text.startswith('nsfw ')
        if nsfw:
            text.replace('nsfw ', '', 1)
        url = await self._get_url(text, nsfw)
        await self.bot.say(f'**{text}**: {url}')


def setup(bot):
    bot.add_cog(Gif(bot))
