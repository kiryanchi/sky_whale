from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Message, Interaction
from wavelink import Player, Playable, TrackSource, Playlist, AutoPlayMode, QueueMode

from setting import INIT_MSG
from sky_whale.embed.help_ui import HelpUi
from sky_whale.embed.music_ui import MusicUi
from sky_whale.embed.search_ui import SearchUi
from sky_whale.util.check import check_player, check_voice
from sky_whale.util.log import Trace, logger

if TYPE_CHECKING:
    from discord import TextChannel, Member
    from sky_whale.extended_bot import ExtendedBot


class Music:
    _player: Player | None = None

    def __init__(
        self, bot: ExtendedBot, channel: TextChannel, message: Message
    ) -> None:
        self.bot = bot
        self.channel = channel
        self.message = message
        self._page = 0
        self._current_position = 0
        self._tmp_position_count = 0

        logger.debug(f"{self}: 생성")

    def __repr__(self) -> str:
        return f"Music(bot: {self.bot}, channel={self.channel}, message={self.message})"

    def __str__(self) -> str:
        return f"Music(Guild: ({self.channel.guild.name}, {self.channel.guild.id}), Channel: ({self.channel.name}, {self.channel.id})"

    @property
    def player(self) -> Player | None:
        return self._player

    @player.setter
    def player(self, player: Player) -> None:
        if not isinstance(player, Player):
            raise TypeError("Player가 아닙니다.")
        player.inactive_timeout = 300
        player.autoplay = AutoPlayMode.partial
        self._player = player
        logger.debug(f"{self}: 플레이어 생성")

    @player.deleter
    def player(self) -> None:
        del self._player
        self._player = None
        logger.debug(f"{self}: 플레이어 삭제")

    @property
    def current_track(self) -> Playable | None:
        if self.player is None:
            return None
        return self.player.current

    @property
    def current_position(self) -> int:
        if self.player is None:
            return 0
        return self._current_position

    @current_position.setter
    def current_position(self, position: int) -> None:
        if position == 0:
            self._tmp_position_count = 0
        self._current_position = position

    @property
    def next_tracks(self) -> list[Playable]:
        if self.player is None:
            return []
        return list(self.player.queue)

    @property
    def is_playing(self) -> bool:
        if self.player is None:
            return False
        return self.player.playing

    @property
    def is_paused(self) -> bool:
        if self.player is None:
            return False
        return self.player.paused

    @property
    def is_autoplaying(self) -> bool:
        if self.player is None:
            return False
        return self.player.autoplay == AutoPlayMode.enabled

    @property
    def current_page(self) -> int:
        return self._page

    @current_page.setter
    def current_page(self, page: int) -> None:
        if page < 0:
            self._page = 0
        elif page > self.max_page:
            self._page = self.max_page
        else:
            self._page = page

    @property
    def max_page(self) -> int:
        if len(self.next_tracks) == 0:
            return 0
        return (len(self.next_tracks) - 1) // 10

    @Trace.command(logger)
    async def play(self, query: str, ctx: Interaction | Message) -> None:
        tracks = await Playable.search(
            query[1:] if query.startswith("!") else query, source=TrackSource.YouTube
        )
        if isinstance(tracks, Playlist):
            await ctx.channel.send(
                "Playlist는 지원하지 않습니다.", delete_after=5, silent=True
            )
            logger.info(f"{self}: '{ctx.author.name}', 플레이리스트: '{query}'")
            return
        if len(tracks) == 0:
            await ctx.channel.send(
                "노래 검색 결과가 없습니다.", delete_after=5, silent=True
            )
            logger.info(f"{self}: '{ctx.author.name}', 노래 검색 실패: '{query}'")
            return

        member: Member = ctx.user if isinstance(ctx, Interaction) else ctx.author

        if not (
            track := (
                tracks[0]
                if len(tracks) == 1 or query.startswith("!")
                else (await self._select_track(query, member, tracks))
            )
        ):
            logger.info(f"{self}: '{ctx.author.name}', 선택 취소")
            return

        track.member = member

        if self.player is None:
            self.player = await member.voice.channel.connect(cls=Player)
            logger.info(f"{self}: '{self.player.channel.name}', 음성 채널 연결")

        await self.player.queue.put_wait(track)
        logger.info(f"{self}: '{ctx.author.name}', 노래 추가: '{track.title}'")

        if not self.player.playing:
            await self.player.play(self.player.queue.get(), volume=30)

        await self.update()

    @check_player
    @check_voice
    @Trace.command(logger)
    async def pause(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        await self.player.pause(not self.is_paused)
        await self.update()
        await interaction.delete_original_response()

    @check_player
    @check_voice
    @Trace.command(logger)
    async def skip(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        await self.player.skip(force=True)
        await self.update()
        await interaction.delete_original_response()

    @check_player
    @check_voice
    @Trace.command(logger)
    async def shuffle(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        self.player.queue.shuffle()
        await self.update()
        await interaction.delete_original_response()

    @check_player
    @check_voice
    @Trace.command(logger)
    async def repeat(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if self.player.queue.mode == QueueMode.loop:
            self.player.queue.mode = QueueMode.normal
        else:
            self.player.queue.mode = QueueMode.loop
        await interaction.delete_original_response()

    @Trace.command(logger)
    async def help(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.edit_original_response(embed=HelpUi.make_ui())

    @check_player
    @Trace.command(logger)
    async def prev_page(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if self.current_page >= 0:
            self.current_page -= 1
            await self.update()
        await interaction.delete_original_response()

    @check_player
    @Trace.command(logger)
    async def next_page(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        if self.current_page < self.max_page:
            self.current_page += 1
            await self.update()
        await interaction.delete_original_response()

    @check_player
    @check_voice
    @Trace.command(logger)
    async def auto(self, interaction: Interaction) -> None:
        if self.player is None:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        if self.player.autoplay == AutoPlayMode.enabled:
            self.player.autoplay = AutoPlayMode.partial
        else:
            self.player.autoplay = AutoPlayMode.enabled
        await self.update()
        await interaction.delete_original_response()

    @check_player
    @check_voice
    @Trace.command(logger)
    async def delete(self, interaction: Interaction) -> None:
        if self.player is None:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.delete_original_response()

    @Trace.command(logger)
    async def reset(self, interaction: Interaction | None = None) -> None:
        if interaction:
            await interaction.response.defer(thinking=True, ephemeral=True)
        await self.player.disconnect()
        del self.player

        await self.channel.purge(after=self.message)
        await self.update()
        if interaction:
            await interaction.delete_original_response()

    async def display_progress(self, position: int) -> None:
        self.current_position = position
        self._tmp_position_count += 1

        if self._tmp_position_count == 2:
            self._tmp_position_count = 0
            await self.update()
            return

    async def update(self) -> None:
        embed, view = MusicUi.make_ui(self)
        await self.message.edit(embed=embed, view=view)

    async def _select_track(
        self, query: str, member: Member, tracks: list[Playable]
    ) -> Playable | None:
        embed, view = await SearchUi.make_ui(query, member, tracks)
        select_msg = await self.channel.send(
            embed=embed, view=view, delete_after=15, silent=True
        )
        logger.debug(f"{self}: '{member.name}', '{query}' 노래 선택 대기")
        if await view.wait():
            logger.debug(f"{self}: '{member.name}', '{query}' 노래 선택 취소")
            return None

        track = view.select_track

        await select_msg.delete()
        logger.debug(f"{self}: '{member.name}', '{query}' 노래 선택: '{track.title}'")
        return track

    @staticmethod
    async def new(bot: ExtendedBot, channel_id: int) -> Music:
        channel = bot.get_channel(channel_id)

        await channel.purge()
        message = await channel.send(content=INIT_MSG, silent=True)

        music = Music(bot, channel, message)
        await music.update()

        return music
