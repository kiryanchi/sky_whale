from __future__ import annotations

from typing import TYPE_CHECKING

from main import bot

if TYPE_CHECKING:
    from discord import Interaction


async def is_administrator(interaction: Interaction) -> bool:
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "서버 관리 권한이 필요해요.", delete_after=5, silent=True
        )
        return False
    return True


async def has_music(interaction: Interaction) -> bool:
    music = bot.musics.get(interaction.guild_id, None)
    if music is None:
        await interaction.response.send_message(
            f"하늘 고래가 없어요. <@{interaction.guild.owner_id}>님에게 `/고래 시작` 명령어를 부탁하세요! ",
        )
        return False
    return True


def check_voice(func):
    async def decorator(*args, **kwargs):
        interaction: Interaction = kwargs.get("interaction")
        if interaction.user.voice is None:
            await interaction.response.send_message(
                "음성 채널에 들어가서 사용해주세요.", delete_after=5, silent=True
            )
            return
        music = bot.musics.get(interaction.guild_id, None)  # player는 무조건 있음
        if music.player.channel != interaction.user.voice.channel:
            await interaction.response.send_message(
                "하늘 고래가 사용 중인 음성 채널에 들어가주세요.",
                delete_after=5,
                silent=True,
            )
            return
        return await func(*args, **kwargs)

    return decorator


def check_player(func):
    async def decorator(*args, **kwargs):
        interaction: Interaction = kwargs.get("interaction")
        music = bot.musics.get(interaction.guild.id, None)
        if music.player is None:
            await interaction.response.send_message(
                "재생 중인 노래가 없어요.", delete_after=5, silent=True
            )
            return
        return await func(*args, **kwargs)

    return decorator
