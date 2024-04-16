from __future__ import annotations
from typing import TYPE_CHECKING, cast

from discord import Message, Interaction
from wavelink import Player, Playable, TrackSource, Playlist, AutoPlayMode, QueueMode

from setting import INIT_MSG
from sky_whale.embed.help_ui import HelpUi
from sky_whale.embed.music_ui import MusicUi
from sky_whale.embed.search import SearchUi
from sky_whale.util import logger

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

    @player.deleter
    def player(self):
        del self._player
        self._player = None

    @property
    def current_track(self) -> Playable | None:
        if self.player is None:
            return None
        return self.player.current

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
        if self.current_track is None:
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

    async def play(self, query: str, ctx: Interaction | Message) -> None:
        tracks = await Playable.search(query, source=TrackSource.YouTube)
        if isinstance(tracks, Playlist):
            await ctx.channel.send(
                "Playlist는 지원하지 않습니다.", delete_after=5, silent=True
            )
            return
        if len(tracks) == 0:
            await ctx.channel.send(
                "노래 검색 결과가 없습니다.", delete_after=5, silent=True
            )
            return

        member: Member = ctx.user if isinstance(ctx, Interaction) else ctx.author

        if not (track := await self._select_track(query, member, tracks)):
            return
        logger.info(f"재생할 노래: {track.title}| {track.author}| {track.member}")

        if not self.player:
            self.player = await member.voice.channel.connect(cls=Player)

        await self.player.queue.put_wait(track)
        if not self.player.playing:
            await self.player.play(self.player.queue.get(), volume=30)

        await self.update()

    async def pause(self, interaction: Interaction) -> None:
        if self.player is None:
            return
        await interaction.response.defer(thinking=True, ephemeral=True)
        await self.player.pause(not self.is_paused)
        await self.update()
        await interaction.delete_original_response()

    async def skip(self, interaction: Interaction) -> None:
        if self.player is None:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        await self.player.skip(force=True)
        await self.update()
        await interaction.delete_original_response()

    async def shuffle(self, interaction: Interaction) -> None:
        if self.player is None:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        self.player.queue.shuffle()
        await self.update()
        await interaction.delete_original_response()

    async def repeat(self, interaction: Interaction) -> None:
        if self.player is None:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        if self.player.queue.mode == QueueMode.loop:
            self.player.queue.mode = QueueMode.normal
        else:
            self.player.queue.mode = QueueMode.loop
        await interaction.delete_original_response()

    async def help(self, interaction: Interaction) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.edit_original_response(embed=HelpUi.make_ui())

    async def prev_page(self, interaction: Interaction) -> None:
        if self.current_page > 0:
            await interaction.response.defer(thinking=True, ephemeral=True)
            self.current_page -= 1
            await self.update()
            await interaction.delete_original_response()

    async def next_page(self, interaction: Interaction) -> None:
        if self.current_page < self.max_page:
            await interaction.response.defer(thinking=True, ephemeral=True)
            self.current_page += 1
            await self.update()
            await interaction.delete_original_response()

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

    async def delete(self, interaction: Interaction) -> None:
        if self.player is None:
            return

        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.delete_original_response()

    async def reset(self, interaction: Interaction | None = None) -> None:
        if self.player is None:
            return

        if interaction:
            await interaction.response.defer(thinking=True, ephemeral=True)
        await self.player.disconnect()
        del self.player

        await self.channel.purge(after=self.message)
        await self.update()
        if interaction:
            await interaction.delete_original_response()

    async def update(self) -> None:
        embed, view = MusicUi.make_ui(self)
        await self.message.edit(embed=embed, view=view)

    async def _select_track(
        self, query: str, member: Member, tracks: list[Playable]
    ) -> Playable | None:
        embed, view = await SearchUi.from_youtube(query, member, tracks)
        select_msg = await self.channel.send(
            embed=embed, view=view, delete_after=15, silent=True
        )
        if await view.wait():
            return None

        track = view.select_track
        track.member = member
        await select_msg.delete()
        return track

    @staticmethod
    async def new(bot: ExtendedBot, channel: TextChannel) -> Music:
        await channel.purge()
        message = await channel.send(content=INIT_MSG, silent=True)

        music = Music(bot, channel, message)
        await music.update()

        return music
