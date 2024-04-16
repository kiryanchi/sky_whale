from __future__ import annotations
from typing import TYPE_CHECKING

from main import bot
from sky_whale.util import logger

if TYPE_CHECKING:
    from discord import Interaction


async def is_administrator(interaction: Interaction) -> bool:
    logger.debug("관리자 체크")
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "서버 관리 권한이 필요해요.", delete_after=5, silent=True
        )
        return False
    return True


async def has_music(interaction: Interaction) -> bool:
    logger.debug("하늘 고래 체크")
    music = bot.musics.get(interaction.guild_id, None)
    if music is None:
        await interaction.response.send_message(
            f"하늘 고래가 없어요. <@{interaction.guild.owner_id}>님에게 `/고래 시작` 명령어를 부탁하세요! ",
        )
        return False
    return True


async def is_in_voice(interaction: Interaction) -> bool:
    logger.debug("음성 채널 체크")
    if interaction.user.voice is None:
        await interaction.response.send_message(
            "음성 채널에 들어가서 사용해주세요.", delete_after=5, silent=True
        )
        return False
    return True


async def has_player(interaction: Interaction) -> bool:
    logger.debug("플레이어 체크")
    music = bot.musics.get(interaction.guild_id, None)
    if music.player is None:
        await interaction.response.send_message(
            "재생 중인 노래가 없어요.", delete_after=5, silent=True
        )
        return False
    return True
