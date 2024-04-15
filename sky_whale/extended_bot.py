import glob
import os

from discord import Intents, Object
from discord.ext.commands import Bot

from sky_whale.util import logger


class ExtendedBot(Bot):

    def __init__(self) -> None:
        super().__init__(intents=Intents.all(), command_prefix="!@#")
        logger.debug(f"Init: Extended Bot (ID: {self.user})")

    async def setup_hook(self) -> None:
        await self._load_cogs()
        await self._sync_cogs()

    async def on_ready(self) -> None:
        logger.info(f"{self.user}가 준비되었습니다.")

    async def _load_cogs(self) -> None:
        num_of_cogs: int = 0
        for cog in glob.glob("sky_whale/cog/*.py"):
            cog = cog[:-3].replace("/", ".")
            await self.load_extension(cog)
            num_of_cogs += 1
            logger.info(f"{cog} Cog를 불러왔습니다.")
        logger.info(f"총 {num_of_cogs}개의 Cog를 불러왔습니다.")

    async def _sync_cogs(self) -> None:
        admin_guild_id = os.environ.get("ADMIN_GUILD_ID")
        logger.debug(f"Admin Guild ID: {admin_guild_id}")
        admin_guild = Object(id=admin_guild_id)
        logger.debug(f"Admin Guild: {admin_guild}")
        self.tree.copy_global_to(guild=admin_guild)
        await self.tree.sync()
        logger.info("Cog 동기화가 완료되었습니다.")
