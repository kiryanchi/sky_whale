from __future__ import annotations
from typing import TYPE_CHECKING, cast

from discord.app_commands import CheckFailure
from discord.ext.commands import GroupCog, Cog
from wavelink import Player, Pool, Playable, TrackSource, TrackEndEventPayload
from discord import app_commands, Message, Interaction

from setting import CHANNEL_NAME
from sky_whale.component.music import Music
from sky_whale.embed.search import SearchUi
from sky_whale.util import logger
from sky_whale.util.check import is_administrator, has_music, is_in_voice

if TYPE_CHECKING:
    from discord import Member
    from wavelink import NodeReadyEventPayload, TrackStartEventPayload
    from sky_whale.extended_bot import ExtendedBot


class MusicCog(GroupCog, name="고래"):

    def __init__(self, bot: ExtendedBot):
        logger.debug("Init: Music Cog")
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        self.bot.musics[750959484477898873] = await Music.new(
            self.bot, self.bot.get_channel(1229745765719605248)
        )
        pass

    @Cog.listener()
    async def on_wavelink_node_ready(self, payload: NodeReadyEventPayload) -> None:
        logger.info(
            f"Wavelink Node 연결됨: {payload.node!r} | Resumed:  {payload.resumed}"
        )

    @Cog.listener()
    async def on_wavelink_track_start(self, payload: TrackStartEventPayload) -> None:
        logger.debug(f"Track End: player: {payload.player} track: {payload.track}")
        await self.bot.musics[payload.player.guild.id].update()

    @Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEndEventPayload) -> None:
        logger.debug(
            f"Track End: player: {payload.player} track: {payload.track} reason: {payload.reason}"
        )
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
    @app_commands.check(has_music)
    @app_commands.check(is_in_voice)
    async def _play(self, interaction: Interaction, query: str) -> None:
        await self.bot.musics[interaction.guild_id].play(query=query, ctx=interaction)
        await interaction.delete_original_response()

    @app_commands.command(name="시작", description="[관리자] 노래 채널을 생성합니다.")
    @app_commands.check(is_administrator)
    async def _start(self, interaction: Interaction) -> None:

        channel = await interaction.guild.create_text_channel(name=CHANNEL_NAME)
        self.bot.musics[interaction.guild_id] = await Music.new(
            self.bot,
            channel,
        )
        logger.info(f"Music Start: {interaction.guild_id}")


async def setup(bot: ExtendedBot) -> None:
    logger.debug("Load Cog: Music")
    await bot.add_cog(MusicCog(bot))
