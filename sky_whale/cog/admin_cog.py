from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Cog

if TYPE_CHECKING:
    from sky_whale.extended_bot import ExtendedBot


class AdminCog(Cog):

    def __init__(self, bot: ExtendedBot) -> None:
        self.bot = bot


async def setup(bot: ExtendedBot) -> None:
    await bot.add_cog(AdminCog(bot))
