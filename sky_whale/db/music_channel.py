from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sky_whale.dto.music_channel_dto import MusicChannelDto


@dataclass(frozen=True)
class MusicChannel:
    guild_id: int
    channel_id: int

    @classmethod
    def from_dto(cls, dto: MusicChannelDto):
        return cls(guild_id=dto["guild_id"], channel_id=dto["channel_id"])
