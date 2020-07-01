import time
import aiohttp
from discord.ext import commands
from discord import Embed


class Astro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sunsigns = [
            "aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
            "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
        ]
        self.api = 'http://horoscope-api.herokuapp.com/horoscope/{when}/{sunsign}'

    async def _get_sunsign(self, sunsign, when):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self.api.format(sunsign=sunsign.lower(), when=when.lower()),
                    params={'t': int(time.time())},
                    timeout=5,
            ) as resp:
                return await resp.json()

    @commands.command(no_pm=True, pass_context=True)
    async def astro(self, ctx):
        """.astro <sign> [today|week|month|year] - Daily dose of bullshit"""
        async with ctx.message.channel.typing():
            message = ctx.message.content.split(' ')

            if len(message) >= 2 and message[1].lower() in self.sunsigns:
                sunsign = message[1]
            else:
                return await ctx.message.channel.send('\n'.join(
                    ['**Command**: astro <sign> [today|week|month|year]',
                    '**Signs**: ' + ', '.join(self.sunsigns)]
                ))

            when = message[2] if len(message) >= 3 and \
                   message[2] in ('today', 'week', 'month', 'year') else 'today'

            horoscope = await self._get_sunsign(sunsign, when)
            embed = Embed(
                title=f'{when}\'s horoscope for {sunsign}',
                type='rich',
                description=horoscope['horoscope'],
            )
            return await ctx.message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Astro(bot))
