import random


class Eightball:
    def __init__(self):
        self.neutral_options = """Reply hazy, try again.
            Ask again later.
            Better not tell you now.
            Cannot predict now.
            Concentrate and ask again.""".split(
            "\n"
        )
        self.negative_options = """Don't count on it.
            My reply is no.
            My sources say no.
            Outlook not so good.
            Very doubtful.""".split(
            "\n"
        )
        self.positive_options = """It is certain.
            It is decidedly so.
            Without a doubt.
            Yes, definitely.
            You may rely on it.
            As I see it, yes.
            Most likely.
            Outlook good.
            Yes.
            Signs point to yes.""".split(
            "\n"
        )
        self.eightball_options = (
            self.positive_options + self.neutral_options + self.negative_options
        )

    async def eightball(self, ctx):
        async with ctx.message.channel.typing():
            if len(ctx.message.content.split(" ")) == 1:
                return await ctx.message.channel.send(
                    "I can't read minds. :disappointed:"
                )
            return await ctx.message.channel.send(random.choice(self.eightball_options))
