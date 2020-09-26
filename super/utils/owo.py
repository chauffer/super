from super.utils import owoify


class Owo:
    async def owo(self, ctx):
        async with ctx.message.channel.typing():
            if len(ctx.message.content.split()) == 1:
                return await ctx.message.channel.send("uwu")
            return await ctx.message.channel.send(
                owoify(" ".join(ctx.message.content.split()[1:]))
            )
