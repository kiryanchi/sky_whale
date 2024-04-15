from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext.commands import Cog

from sky_whale.util import logger

if TYPE_CHECKING:
    from sky_whale.extended_bot import ExtendedBot


class AdminCog(Cog):

    def __init__(self, bot: ExtendedBot) -> None:
        logger.debug("Init: Admin Cog")
        self.bot = bot


async def setup(bot: ExtendedBot) -> None:
    logger.debug("Load Cog: Admin")
    await bot.add_cog(AdminCog(bot))
