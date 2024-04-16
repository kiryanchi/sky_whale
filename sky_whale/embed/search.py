from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed, ui, ButtonStyle

from setting import DEFAULT_IMG, NUM_OF_SEARCH
from sky_whale.util import logger
from sky_whale.util.string import ms_to_str

if TYPE_CHECKING:
    from discord import Member, Interaction
    from wavelink import Playable


class SearchUi:
    class Embed(Embed):

        def __init__(self, query: str, member: Member, tracks: list[Playable]) -> None:
            super().__init__(
                title=f"검색: {query}", description=f"<@{member.id}>님이 검색했습니다!"
            )
            self.set_thumbnail(url=DEFAULT_IMG)

            nums_emoji = {
                1: ":one:",
                2: ":two:",
                3: ":three:",
                4: ":four:",
                5: ":five:",
                6: ":six:",
                7: ":seven:",
                8: ":eight:",
                9: ":nine:",
                10: ":keycap_ten:",
            }

            for idx, track in enumerate(tracks):
                self.add_field(
                    name=f"{nums_emoji[idx + 1]}\t({ms_to_str(track.length)}) {track.author}",
                    value=f"{track.title}",
                    inline=False,
                )

    class View(ui.View):
        select_track: Playable

        def __init__(self, member: Member, tracks: list[Playable]) -> None:
            super().__init__()
            self.member = member
            self.tracks = tracks

            for i in range(len(tracks) // 5 + 1):
                for j in range(1, 6):
                    if i * 5 + j - 1 < len(tracks):
                        self.add_item(SearchUi.Button(label=str(i * 5 + j), row=i))

    class Button(ui.Button[View]):

        def __init__(self, label: str, row: int):
            super().__init__(style=ButtonStyle.secondary, label=label, row=row)

        async def callback(self, interaction: Interaction) -> None:
            assert self.view is not None

            if interaction.user != self.view.member:
                return await interaction.response.send_message(
                    content="쉿! 신청자만 선택할 수 있어요...!",
                    ephemeral=True,
                    delete_after=5,
                )

            self.view.select_track = self.view.tracks[int(self.label) - 1]
            self.view.stop()

    @staticmethod
    async def from_youtube(
        query: str, member: Member, tracks: list[Playable]
    ) -> tuple[Embed, View]:
        num_elements = min(len(tracks), NUM_OF_SEARCH)
        tracks = tracks[:num_elements]

        embed = SearchUi.Embed(query=query, member=member, tracks=tracks)
        view = SearchUi.View(member=member, tracks=tracks)

        return embed, view
