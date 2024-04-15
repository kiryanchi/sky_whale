from __future__ import annotations
from typing import TYPE_CHECKING

from wavelink import Player

from sky_whale.util import logger

if TYPE_CHECKING:
    from discord import TextChannel, Message
    from sky_whale.extended_bot import ExtendedBot


class Music:
    _player: Player | None = None

    def __init__(
        self, bot: ExtendedBot, channel: TextChannel, message: Message
    ) -> None:
        self.bot = bot
        self.channel = channel
        self.message = message

    @property
    def player(self) -> Player | None:
        return self._player

    @player.setter
    def player(self, player: Player) -> None:
        if not isinstance(player, Player):
            raise TypeError("Player가 아닙니다.")
        player.inactive_timeout = 300
        self._player = player

    async def update(self) -> None:
        return

    @staticmethod
    async def new(bot: ExtendedBot, channel: TextChannel) -> Music:
        message = await channel.send("음악 채널이 생성되었습니다.")

        music = Music(bot, channel, message)
        await music.update()

        return music
