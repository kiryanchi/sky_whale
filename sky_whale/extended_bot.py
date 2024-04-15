from discord import Intents
from discord.ext.commands import Bot


class ExtendedBot(Bot):

    def __init__(self) -> None:
        super().__init__(intents=Intents.all(), command_prefix="!")

    def on_ready(self) -> None:
        print(f"Logged in as {self.user}")
