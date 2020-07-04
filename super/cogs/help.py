from contextlib import suppress
import itertools
from discord import Embed
from discord.ext.commands import HelpCommand, Command, Cog, Bot
from super.settings import SUPER_HELP_COLOR


class CustomHelpCommand(HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={"help": "**.help** - Shows help for bot commands."}
        )

    async def command_formatting(self, command: Command) -> Embed:
        """
        Takes the command help and turns it into Embed
        """
        embed = Embed()
        embed.set_author(name="Command Help")

        command_details = f"{command.help or 'No details provided.'}\n"
        embed.description = command_details

        return embed

    async def send_command_help(self, command: Command) -> None:
        """
        Sends help message for single command
        """
        embed = await self.command_formatting(command)
        await self.context.send(embed=embed)

    @staticmethod
    def _category_key(command: Command) -> str:
        """
        Returns cog class name of given command for sorting.
        """
        if command.cog:
            with suppress(AttributeError):
                if command.cog.category:
                    return f"**{command.cog.category}**"
            return f"**{command.cog_name}**"
        return "**\u200bNo Category:**"

    async def send_bot_help(self, mapping: dict) -> None:
        """
        Send help for all bot commands
        """

        embed = Embed(color=SUPER_HELP_COLOR, type="rich")
        embed.set_author(name="List of Commands")
        embed.set_thumbnail(url=self.context.bot.user.avatar_url)
        embed.set_image(url=self.context.bot.user.avatar.url)

        filter_commands = await self.filter_commands(
            self.context.bot.commands, sort=True, key=self._category_key
        )

        for _commands in itertools.groupby(filter_commands, key=self._category_key):
            # _commands is a tuple : (<Cog Class Name>, <commands>)
            commands = sorted(_commands[1], key=lambda c: c.name)
            if len(commands) == 0:
                continue
            embed.add_field(
                name=commands[0].cog.description
                if _commands[0] != "**Help**"
                else "Command List",
                value="\n".join([command.short_doc for command in commands]),
                inline=False,
            )
        await self.context.send(embed=embed)


class Help(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.old_help_command = bot.help_command
        custom_help_cmd = CustomHelpCommand()
        bot.help_command = custom_help_cmd
        bot.help_command.cog = self

    def cog_unload(self) -> None:
        """
        Restore old help command when CustomHelpCommand is deleted or doesn't work
        """
        self.bot.help_command = self.old_help_command


def setup(bot: Bot) -> None:
    bot.add_cog(Help(bot))
