import glob
import os

from discord import Intents, Object
from discord.ext.commands import Bot


class ExtendedBot(Bot):

    def __init__(self) -> None:
        super().__init__(intents=Intents.all(), command_prefix="!")

    async def setup_hook(self) -> None:
        await self._load_cogs()
        await self._sync_cogs()

    def on_ready(self) -> None:
        print(f"Logged in as {self.user}")

    async def _load_cogs(self) -> None:
        for cog in glob.glob("sky_whale/cog/*.py"):
            cog = cog[:-3].replace("/", ".")
            await self.load_extension(cog)

    async def _sync_cogs(self) -> None:
        admin_guild = Object(os.environ.get("ADMIN_GUILD_ID"))
        self.tree.copy_global_to(guild=admin_guild)
        await self.tree.sync()
