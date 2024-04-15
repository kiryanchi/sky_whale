from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed, ui, ButtonStyle

from setting import DEFAULT_IMG, NUM_OF_SEARCH
from sky_whale.search.youtube import search_from_youtube
from sky_whale.util import logger

if TYPE_CHECKING:
    from discord import User, Interaction
    from sky_whale.search.youtube import Video


class SearchUi:
    class Embed(Embed):

        def __init__(self, query: str, user: User, videos: list[Video]) -> None:
            super().__init__(
                title=f"검색: {query}", description=f"<@{user.id}>님이 검색했습니다!"
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

            for idx, video in enumerate(videos):
                self.add_field(
                    name=f"{nums_emoji[idx + 1]}\t({video.duration}) {video.uploader}",
                    value=f"{video.title}",
                    inline=False,
                )

    class View(ui.View):

        def __init__(self, user: User, videos: list[Video]) -> None:
            super().__init__()
            self.user = user
            self.videos = videos
            self.link: str = ""

            for i in range(NUM_OF_SEARCH // 5 + 1):
                for j in range(1, 6):
                    if i * 5 + j - 1 < NUM_OF_SEARCH:
                        self.add_item(SearchUi.Button(label=str(i * 5 + j), row=i))

    class Button(ui.Button[View]):

        def __init__(self, label: str, row: int):
            super().__init__(style=ButtonStyle.secondary, label=label, row=row)

        async def callback(self, interaction: Interaction) -> None:
            assert self.view is not None

            if interaction.user != self.view.user:
                return await interaction.response.send_message(
                    content="쉿! 신청자만 선택할 수 있어요...!",
                    ephemeral=True,
                    delete_after=5,
                )

            self.view.link = self.view.videos[int(self.label) - 1].link
            self.view.stop()

    @staticmethod
    async def from_youtube(query: str, user: User) -> tuple[Embed, View]:
        try:
            videos = await search_from_youtube(query=query)

            embed = SearchUi.Embed(query=query, user=user, videos=videos)
            view = SearchUi.View(user=user, videos=videos)

            return embed, view

        except ValueError as e:
            logger.exception(e)
