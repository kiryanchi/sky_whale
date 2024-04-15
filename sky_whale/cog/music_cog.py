from __future__ import annotations
from typing import TYPE_CHECKING, cast

from discord.app_commands import CheckFailure
from discord.ext.commands import GroupCog, Cog
from wavelink import Player, Pool
from discord import app_commands, Message, Interaction

from setting import CHANNEL_NAME
from sky_whale.component.music import Music
from sky_whale.embed.search import SearchUi
from sky_whale.util import logger
from sky_whale.util.check import is_administrator, has_music, is_in_voice

if TYPE_CHECKING:
    from discord import Member
    from wavelink import NodeReadyEventPayload
    from sky_whale.extended_bot import ExtendedBot


class MusicCog(GroupCog, name="고래"):

    def __init__(self, bot: ExtendedBot):
        logger.debug("Init: Music Cog")
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        pass

    @Cog.listener()
    async def on_wavelink_node_ready(self, payload: NodeReadyEventPayload) -> None:
        logger.info(
            f"Wavelink Node 연결됨: {payload.node!r} | Resumed:  {payload.resumed}"
        )

    @Cog.listener()
    async def on_wavelink_inactive_player(self, player: Player) -> None:
        await player.channel.send("음악 재생이 중지되었습니다.")
        await player.disconnect()

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.bot:
            return

        if not (music := self.bot.musics.get(message.guild.id, None)):
            return

        if music.channel.id != message.channel.id:
            return

        if message.author.voice is None:
            return

        link: str = ""
        embed, view = await SearchUi.from_youtube(
            query=message.content, user=message.author
        )

        select_msg = await message.channel.send(
            embed=embed, view=view, delete_after=15, silent=True
        )

        if not await view.wait():
            link = view.link
            await select_msg.delete()

        # TODO: Music Play
        await self._play(link=link, ctx=message)
        logger.info(f"Link: {link}")

    @app_commands.command(name="재생", description="노래를 재생합니다.")
    @app_commands.rename(query="노래")
    @app_commands.describe(query="노래 제목ㆍ유튜브 링크")
    @app_commands.check(has_music)
    @app_commands.check(is_in_voice)
    async def _pla(self, interaction: Interaction, query: str) -> None:
        await self._play(link=query, ctx=interaction)

    @app_commands.command(name="시작", description="[관리자] 노래 채널을 생성합니다.")
    @app_commands.check(is_administrator)
    async def _start(self, interaction: Interaction) -> None:

        channel = await interaction.guild.create_text_channel(name=CHANNEL_NAME)
        self.bot.musics[interaction.guild_id] = await Music.new(
            self.bot,
            channel,
        )
        logger.info(f"Music Start: {interaction.guild_id}")

    async def _play(self, link: str, ctx: Interaction | Message) -> None:
        member: Member
        player: Player | None

        if isinstance(ctx, Interaction):
            logger.debug("Interaction")
            member = ctx.user
        else:
            logger.debug("Message")
            member = ctx.author

        player = self.bot.musics.get(member.guild.id, None).player
        player = cast(Player, player)

        if not player:
            player = await member.voice.channel.connect(cls=Player)
            self.bot.musics[member.guild.id].player = player

        tracks = await Pool.fetch_tracks(link)
        if not tracks:
            logger.info("Track Not Found")
            return
        logger.debug(f"Track: {tracks}, length: {len(tracks)}")
        track = tracks[0]
        await player.queue.put_wait(track)
        logger.info(f"Track: {track} Queue")

        if not player.playing:
            await player.play(player.queue.get(), volume=30)


async def setup(bot: ExtendedBot) -> None:
    logger.debug("Load Cog: Music")
    await bot.add_cog(MusicCog(bot))
