positive_options = """It is certain.
It is decidedly so.
Without a doubt.
Yes, definitely.
You may rely on it.
As I see it, yes.
Most likely.
Outlook good.
Yes.
Signs point to yes.""".split("\n")

netural_options = """Reply hazy, try again.
Ask again later.
Better not tell you now.
Cannot predict now.
Concentrate and ask again.""".split("\n")

negative_options = """Don't count on it.
My reply is no.
My sources say no.
Outlook not so good.
Very doubtful.""".split("\n")

eightball_options = positive_options + netural_options + negative_options
