from discord.ext import commands
from aiogoogletrans import Translator
from aiogoogletrans.constants import LANGUAGES
import structlog

logger = structlog.getLogger(__name__)


class Translate:

    def is_language(self, text):
        return text in LANGUAGES.keys()

    async def translate(self, words):
        config = {"from": "auto", "to": "en"}
        for _ in range(2):
            if len(words) < 3:
                continue
            setting, value = words[0], words[1]
            if words[0] not in ("from", "to") or not self.is_language(value):
                continue

            config[setting] = value
            del words[0:2]

        logger.debug("utils/translate/translate: Translating", words=" ".join(words))
        out = await Translator().translate(
            text=" ".join(words), src=config["from"], dest=config["to"],
        )
        logger.info(
            "cogs/translate/transalte: Translated",
            src=out.src,
            dest=out.dest,
            text=out.text,
        )
        return f"**{out.src}**→**{out.dest}** - {out.text}"

    async def t(self, msg):
        message = msg.split()[1:]
        if not message:
            return "**.t** [from lang] [to lang] <sentence>. Auto detects by default."
        return await self.translate(message)
