from __future__ import annotations

from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext.commands import GroupCog, Cog
from wavelink import Player

from setting import CHANNEL_NAME
from sky_whale.component.music import Music
from sky_whale.db.music_channel import MusicChannel
from sky_whale.util import logger
from sky_whale.util.check import is_administrator, has_music

if TYPE_CHECKING:
    from discord import Message, Interaction, Member, VoiceState
    from wavelink import (
        NodeReadyEventPayload,
        TrackEndEventPayload,
        PlayerUpdateEventPayload,
        TrackStartEventPayload,
    )
    from sky_whale.extended_bot import ExtendedBot


class MusicCog(GroupCog, name="고래"):

    def __init__(self, bot: ExtendedBot) -> None:
        self.bot = bot

        logger.debug("[클래스] MusicCog 생성")

    @Cog.listener()
    async def on_voice_state_update(
        self, member: Member, before: VoiceState, after: VoiceState
    ) -> None:
        if before.channel is None:
            return
        if music := self.bot.musics.get(member.guild.id, None):
            # 봇인 경우
            if member.id == self.bot.user.id:
                if after.channel is None:
                    return
                if (
                    self.bot.user in after.channel.members
                    and len([user for user in after.channel.members if not user.bot])
                    == 0
                ):
                    await music.reset()
                return
            # 유저인 경우
            if (
                self.bot.user in before.channel.members
                and len([user for user in before.channel.members if not user.bot]) == 0
            ):
                await music.reset()
                return

    @Cog.listener()
    async def on_ready(self) -> None:
        music_channels = self.bot.db_connector.fetch_all()
        for music_channel in music_channels:
            guild = self.bot.get_guild(music_channel.guild_id)
            channel = self.bot.get_channel(music_channel.channel_id)
            if guild and channel:
                self.bot.musics[music_channel.guild_id] = await Music.new(
                    self.bot, music_channel.channel_id
                )
            else:
                self.bot.db_connector.delete(music_channel.guild_id)
        logger.info("모든 노래 채널을 불러왔습니다.")

    @Cog.listener()
    async def on_wavelink_node_ready(self, payload: NodeReadyEventPayload) -> None:
        logger.info(f"Wavelink 노드가 준비되었습니다. {payload.node!r}")

    @Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackStartEventPayload) -> None:
        if music := self.bot.musics.get(payload.player.guild.id, None):
            logger.info(f"{music}: 노래 재생: '{payload.track.title}'")

    @Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEndEventPayload) -> None:
        if payload.player is None:
            return
        if payload.player.queue.is_empty:
            await self.bot.musics[payload.player.guild.id].update()

    @Cog.listener()
    async def on_wavelink_player_update(
        self, payload: PlayerUpdateEventPayload
    ) -> None:
        if payload.player is None:
            return
        if music := self.bot.musics.get(payload.player.guild.id, None):
            await music.display_progress(payload.position)

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
    @app_commands.check(has_music)
    async def _play(self, interaction: Interaction, query: str) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        await self.bot.musics[interaction.guild_id].play(query=query, ctx=interaction)
        await interaction.delete_original_response()

    @app_commands.command(name="시작", description="[관리자] 노래 채널을 생성합니다.")
    @app_commands.check(is_administrator)
    async def _start(self, interaction: Interaction) -> None:
        if interaction.guild_id in self.bot.musics:
            self.bot.db_connector.delete(interaction.guild_id)

        await interaction.response.defer(thinking=True)
        channel = await interaction.guild.create_text_channel(name=CHANNEL_NAME)
        self.bot.musics[interaction.guild_id] = await Music.new(
            self.bot,
            channel.id,
        )
        await interaction.delete_original_response()

        music_channel = MusicChannel(
            guild_id=interaction.guild_id, channel_id=channel.id
        )
        self.bot.db_connector.insert(music_channel)

    @app_commands.command(name="정지", description="노래를 일시정지/재생 합니다.")
    @app_commands.check(has_music)
    async def _pause(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].pause(interaction=interaction)

    @app_commands.command(name="스킵", description="노래를 스킵합니다.")
    @app_commands.check(has_music)
    async def _skip(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].skip(interaction=interaction)

    @app_commands.command(name="셔플", description="재생목록을 섞습니다.")
    @app_commands.check(has_music)
    async def _shuffle(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].shuffle(interaction=interaction)

    @app_commands.command(name="반복", description="한곡을 반복합니다.")
    @app_commands.check(has_music)
    async def _loop(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].loop(interaction=interaction)

    @app_commands.command(name="도움말", description="고래의 사용법을 알려줍니다.")
    @app_commands.check(has_music)
    async def _help(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].help(interaction=interaction)

    @app_commands.command(name="자동", description="다음 곡을 자동으로 가져옵니다.")
    @app_commands.check(has_music)
    async def _auto(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].auto(interaction=interaction)

    @app_commands.command(name="삭제", description="노래를 삭제합니다.")
    @app_commands.check(has_music)
    async def _delete(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].delete(interaction=interaction)

    @app_commands.command(name="초기화", description="노래를 초기화합니다.")
    @app_commands.check(has_music)
    async def _reset(self, interaction: Interaction) -> None:
        await self.bot.musics[interaction.guild_id].reset(interaction=interaction)


async def setup(bot: ExtendedBot) -> None:
    await bot.add_cog(MusicCog(bot))
