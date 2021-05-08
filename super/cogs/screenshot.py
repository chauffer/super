import os
import traceback
from tempfile import _get_candidate_names, gettempdir

import aiohttp

import pyppeteer
from aiocache import Cache, cached
from discord import File
from discord.ext import commands
from furl import furl
from super.utils import R


class Screenshot(commands.Cog):
    """Screenshot a web page"""

    def __init__(self, bot):
        self.bot = bot

    async def _screenshot(self, url, client, full=False):
        url = furl(url).add({"on_behalf_of_discord_clientid": client}).url

        browser = await pyppeteer.launch(
            executablePath="/usr/bin/chromium-browser",
            args=["--no-sandbox", "--window-size=1920,1080", "--start-maximized"],
        )
        page = await browser.newPage()
        await page.setViewport({"width": 1920, "height": 1080})
        await page.goto(url, waitUntil=["networkidle0", "domcontentloaded"])
        path = os.path.join(gettempdir(), next(_get_candidate_names()))
        await page.screenshot({"path": path, "fullPage": full, "type": "png"})
        await browser.close()

        with open(path, "rb") as f:
            return path, File(f, filename=f"screenshot_{client}.png")

    @commands.command(no_pm=True, pass_context=True)
    async def screenshot(self, ctx):
        """**.screenshot** <url> [full] - Screenshot a page"""

        async with ctx.message.channel.typing():
            if len(ctx.message.content.split()) == 1:
                return await ctx.message.channel.send("Usage: .screenshot <url> [full]")
            message = ctx.message.content.split()
            try:
                path, file = await self._screenshot(
                    message[1],
                    ctx.message.author.id,
                    True if len(message) >= 2 else False,
                )
            except:
                return await ctx.message.channel.send(
                    ":thinking:\n " + traceback.format_exc()
                )

            msg = await ctx.message.channel.send(file=file)
            os.unlink(path)
            return msg


def setup(bot):
    bot.add_cog(Screenshot(bot))
