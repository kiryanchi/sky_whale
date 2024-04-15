from __future__ import annotations
from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext.commands import GroupCog, Cog

from sky_whale.embed.search import SearchUi
from sky_whale.util import logger

if TYPE_CHECKING:
    from discord import Message, Interaction
    from sky_whale.extended_bot import ExtendedBot


class MusicCog(GroupCog, name="고래"):

    def __init__(self, bot: ExtendedBot):
        logger.debug("Init: Music Cog")
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        link: str = ""
        embed, view = await SearchUi.from_youtube(
            query=message.content, user=message.author
        )

        select_msg = await message.channel.send(
            embed=embed, view=view, delete_after=15, silent=True
        )

        if not await view.wait():
            link = view.link
            await select_msg.delete()

        # TODO: Music Play
        logger.info(f"Link: {link}")


async def setup(bot: ExtendedBot) -> None:
    logger.debug("Load Cog: Music")
    await bot.add_cog(MusicCog(bot))
