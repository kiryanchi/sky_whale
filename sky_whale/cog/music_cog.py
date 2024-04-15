from __future__ import annotations
from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext.commands import GroupCog, Cog

if TYPE_CHECKING:
    from discord import Message, Interaction
    from sky_whale.extended_bot import ExtendedBot


class MusicCog(GroupCog, name="고래"):

    def __init__(self, bot: ExtendedBot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        # search music in YouTube


async def setup(bot: ExtendedBot) -> None:
    await bot.add_cog(MusicCog(bot))
