from __future__ import annotations

import glob
import os
from typing import TYPE_CHECKING

from discord import Intents, Object
from discord.ext.commands import Bot
from wavelink import Pool, Node

from sky_whale.db.music_channel import MusicChannel
from sky_whale.util.log import Trace, logger

if TYPE_CHECKING:
    from discord import Guild
    from sky_whale.component.music import Music


@Trace.init(logger)
class ExtendedBot(Bot):
    __instance = None
    musics: dict[int, Music] = {}

    def __init__(self) -> None:
        super().__init__(intents=Intents.all(), command_prefix="!@#")

    async def setup_hook(self) -> None:
        await self._load_cogs()
        await self._sync_cogs()
        await self._connect_nodes()

    async def on_ready(self) -> None:
        pass

    async def on_guild_remove(self, guild: Guild):
        await MusicChannel.delete(guild.id)

    async def _load_cogs(self) -> None:
        num_of_cogs: int = 0
        for cog in glob.glob("sky_whale/cog/*.py"):
            cog = cog[:-3].replace("/", ".")
            await self.load_extension(cog)
            num_of_cogs += 1

    async def _sync_cogs(self) -> None:
        admin_guild_id = os.environ.get("ADMIN_GUILD_ID")
        admin_guild = Object(id=admin_guild_id)
        self.tree.copy_global_to(guild=admin_guild)
        await self.tree.sync(guild=admin_guild)

        await self.tree.sync()

    async def _connect_nodes(self) -> None:
        wavelink_uri = os.environ.get("WAVELINK_URI")
        wavelink_password = os.environ.get("WAVELINK_PASSWORD")

        await Pool.connect(
            nodes=[Node(uri=wavelink_uri, password=wavelink_password)],
            client=self,
            cache_capacity=100,
        )

    @classmethod
    def get_instance(cls) -> ExtendedBot:
        if cls.__instance is None:
            cls.__instance = ExtendedBot()
        return cls.__instance
