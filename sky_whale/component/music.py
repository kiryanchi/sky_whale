from __future__ import annotations
from typing import TYPE_CHECKING, cast

from discord import Message, Interaction
from wavelink import Player, Playable, TrackSource, Playlist

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

    @property
    def player(self) -> Player | None:
        return self._player

    @player.setter
    def player(self, player: Player) -> None:
        if not isinstance(player, Player):
            raise TypeError("Player가 아닙니다.")
        player.inactive_timeout = 300
        self._player = player

    async def play(self, query: str, ctx: Interaction | Message):
        member: Member

        if isinstance(ctx, Interaction):
            member = ctx.user
        else:
            member = ctx.author

        tracks = await Playable.search(query, source=TrackSource.YouTube)
        if isinstance(tracks, Playlist):
            logger.debug("Playlist은 지원하지 않습니다.")
            return

        tracks = cast(list[Playable], tracks)
        track: Playable | None = None

        if len(tracks) == 0:
            logger.info("노래 검색 결과가 없습니다.")
            return
        elif len(tracks) == 1:
            track = tracks[0]
        else:
            # Select a song
            embed, view = await SearchUi.from_youtube(query, member, tracks)
            select_msg = await self.channel.send(embed=embed, view=view)
            if not await view.wait():
                track = view.select_track
                await select_msg.delete()

        if not self.player:
            self.player = await member.voice.channel.connect(cls=Player)

        await self.player.queue.put_wait(track)
        if not self.player.playing:
            await self.player.play(self.player.queue.get(), volume=30)

    async def update(self) -> None:
        return

    @staticmethod
    async def new(bot: ExtendedBot, channel: TextChannel) -> Music:
        message = await channel.send("음악 채널이 생성되었습니다.")

        music = Music(bot, channel, message)
        await music.update()

        return music
