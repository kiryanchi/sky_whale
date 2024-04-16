from __future__ import annotations

from typing import TYPE_CHECKING

from discord import app_commands, Message, Interaction
from discord.ext.commands import GroupCog, Cog
from wavelink import Player, TrackEndEventPayload

from setting import CHANNEL_NAME
from sky_whale.component.music import Music
from sky_whale.db.music_channel import MusicChannel
from sky_whale.util import logger
from sky_whale.util.check import is_administrator, has_music, is_in_voice, has_player

if TYPE_CHECKING:
    from wavelink import NodeReadyEventPayload, TrackStartEventPayload
    from sky_whale.extended_bot import ExtendedBot


class MusicCog(GroupCog, name="고래"):

    def __init__(self, bot: ExtendedBot):
        logger.debug("Init: Music Cog")
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        music_channels = await MusicChannel.get_all()
        for music_channel in music_channels:
            self.bot.musics[music_channel.guild_id] = await Music.new(
                self.bot, music_channel.channel_id
            )
            logger.info(
                f"{str(self.bot.musics[music_channel.guild_id])} 채널 준비 완료"
            )

    @Cog.listener()
    async def on_wavelink_node_ready(self, payload: NodeReadyEventPayload) -> None:
        logger.info(
            f"Wavelink Node 연결됨: {payload.node!r} | Resumed:  {payload.resumed}"
        )

    @Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackStartEventPayload) -> None:
        logger.debug(f"Track Start: player: {payload.player} track: {payload.track}")
        await self.bot.musics[payload.player.guild.id].update()

    @Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEndEventPayload) -> None:
        logger.debug(
            f"Track End: player: {payload.player} track: {payload.track} reason: {payload.reason}"
        )
        if payload.player is None:
            return
        if payload.player.queue.is_empty:
            await self.bot.musics[payload.player.guild.id].update()

    @Cog.listener()
    async def on_wavelink_inactive_player(self, player: Player) -> None:
        await self.bot.musics[player.guild.id].reset()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        if not (music := self.bot.musics.get(message.guild.id, None)):
            return

        if music.channel.id != message.channel.id:
            return

        if message.author.voice is None:
            await message.channel.send(
                "음성 채널에 들어가서 사용해주세요.", delete_after=5, silent=True
            )
            await message.delete()
            return

        await music.play(query=message.content, ctx=message)
        await message.delete()

    @app_commands.command(name="재생", description="노래를 재생합니다.")
    @app_commands.rename(query="노래")
    @app_commands.describe(query="노래 제목ㆍ유튜브 링크")
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _play(self, interaction: Interaction, query: str) -> None:
        await self.bot.musics[interaction.guild_id].play(query=query, ctx=interaction)
        await interaction.delete_original_response()

    @app_commands.command(name="시작", description="[관리자] 노래 채널을 생성합니다.")
    @app_commands.check(is_administrator)
    async def _start(self, interaction: Interaction) -> None:

        channel = await interaction.guild.create_text_channel(name=CHANNEL_NAME)
        self.bot.musics[interaction.guild_id] = await Music.new(
            self.bot,
            channel.id,
        )
        logger.info(f"Music Start: {interaction.guild_id}")

    @app_commands.command(name="정지", description="노래를 일시정지/재생 합니다.")
    @app_commands.check(has_player)
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _pause(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].pause(interaction)

    @app_commands.command(name="스킵", description="노래를 스킵합니다.")
    @app_commands.check(has_player)
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _skip(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].skip(interaction)

    @app_commands.command(name="셔플", description="재생목록을 섞습니다.")
    @app_commands.check(has_player)
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _shuffle(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].shuffle(interaction)

    @app_commands.command(name="반복", description="한곡을 반복합니다.")
    @app_commands.check(has_player)
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _repeat(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].repeat(interaction)

    @app_commands.command(name="도움말", description="고래의 사용법을 알려줍니다.")
    @app_commands.check(has_music)
    async def _help(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].help(interaction)

    @app_commands.command(name="자동", description="다음 곡을 자동으로 가져옵니다.")
    @app_commands.check(has_player)
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _auto(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].auto(interaction)

    @app_commands.command(name="삭제", description="노래를 삭제합니다.")
    @app_commands.check(has_player)
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _delete(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].delete(interaction)

    @app_commands.command(name="초기화", description="노래를 초기화합니다.")
    @app_commands.check(is_in_voice)
    @app_commands.check(has_music)
    async def _reset(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].reset(interaction)


async def setup(bot: ExtendedBot) -> None:
    logger.debug("Load Cog: Music")
    await bot.add_cog(MusicCog(bot))
