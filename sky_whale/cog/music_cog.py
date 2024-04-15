from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext.commands import GroupCog

if TYPE_CHECKING:
    from sky_whale.extended_bot import ExtendedBot


class MusicCog(GroupCog, name="고래"):

    def __init__(self, bot: ExtendedBot):
        self.bot = bot


async def setup(bot: ExtendedBot) -> None:
    await bot.add_cog(MusicCog(bot))
