from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed, ui, ButtonStyle

from setting import DEFAULT_IMG, DEFAULT_DELETE_COLOR
from sky_whale.util.string import ms_to_str

if TYPE_CHECKING:
    from discord import Member, Interaction
    from wavelink import Playable


class DeleteUi:
    class Embed(Embed):

        def __init__(self, member: Member, tracks: list[Playable]) -> None:
            super().__init__(
                title=f"삭제할 노래를 선택해주세요.",
                description=f"<@{member.id}>님이 삭제합니다!",
                color=DEFAULT_DELETE_COLOR,
            )
            self.set_thumbnail(url=DEFAULT_IMG)

            for idx, track in enumerate(tracks):
                self.add_field(
                    name=f"{idx + 1}\t({ms_to_str(track.length)}) {track.author}",
                    value=f"{track.title}",
                    inline=False,
                )

    class View(ui.View):
        idx: int = -1

        def __init__(self, member: Member, tracks: list[Playable]) -> None:
            super().__init__(timeout=15)
            self.member = member
            self.tracks = tracks

            for i in range(len(tracks) // 5 + 1):
                for j in range(1, 6):
                    if i * 5 + j - 1 < len(tracks):
                        self.add_item(DeleteUi.Button(label=str(i * 5 + j), row=i))

    class Button(ui.Button[View]):

        def __init__(self, label: str, row: int) -> None:
            super().__init__(style=ButtonStyle.secondary, label=label, row=row)

        async def callback(self, interaction: Interaction) -> None:
            assert self.view is not None

            if interaction.user != self.view.member:
                return await interaction.response.send_message(
                    content="쉿! 신청자만 선택할 수 있어요...!",
                    ephemeral=True,
                    delete_after=5,
                )

            self.view.idx = int(self.label) - 1
            self.view.stop()

    @staticmethod
    async def make_ui(member: Member, tracks: list[Playable]) -> tuple[Embed, View]:
        embed = DeleteUi.Embed(member=member, tracks=tracks)
        view = DeleteUi.View(member=member, tracks=tracks)

        return embed, view
