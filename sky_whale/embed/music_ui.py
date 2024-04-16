from __future__ import annotations

import re
from typing import TYPE_CHECKING

from discord import Embed, ui, ButtonStyle

from setting import (
    DEFAULT_COLOR,
    DEFAULT_IMG,
    DEFAULT_DISCORD_INVITE_URL,
    DEFAULT_DISCORD_GUILD_URL,
)
from sky_whale.util.string import ms_to_str

if TYPE_CHECKING:
    from discord import Interaction
    from sky_whale.component.music import Music


def wrap(text: str) -> str:
    def is_korean(character):
        hangul = re.compile("[^ㄱ-ㅣ가-힣]+")
        result = hangul.sub("", character)
        return result != ""

    word_cnt = 0
    result_text = ""
    for char in text:
        if word_cnt > 42:
            result_text += "..."
            break

        if is_korean(char):
            word_cnt += 2
        else:
            word_cnt += 1

        result_text += char
    return result_text


class MusicUi:
    class Embed(Embed):
        space = "ㅤ"
        bold_line = "━"
        thin_line = "─"
        dot = "●"

        def __init__(self, music: Music):
            self.music = music

            super().__init__(
                title=f" 🐳{self.space}Sky Whale{self.space} 🐳",
                color=DEFAULT_COLOR,
                url=DEFAULT_DISCORD_GUILD_URL,
            )

            self.set_image(url=self.image_url).set_author(
                name="하늘 고래를 서버로 불러보세요!",
                url=DEFAULT_DISCORD_INVITE_URL,
                icon_url=DEFAULT_IMG,
            ).set_footer(
                text=f"현재 페이지{self.space}{self.music.current_page + 1}/{self.space}{self.music.max_page + 1}"
            )

            self.add_field(
                name=f"🎵{self.space}현재 재생중인 노래",
                value=self.current_track_message,
                inline=False,
            )

            if self.music.current_track:
                self.add_field(
                    name=f"📌{self.space}채널",
                    value=self.music.current_track.author,
                    inline=True,
                )
                if self.music.current_track.recommended:
                    self.add_field(
                        name=f"🤖{self.space}분석... 완료",
                        value="자동 재생 중",
                        inline=True,
                    )
                else:
                    self.add_field(
                        name=f"🤷‍♀️{self.space}이거 누가 넣음?",
                        value=f"<@{self.music.current_track.member.id}>",
                        inline=True,
                    )

            self.add_field(
                name=f"📚{self.space}대기중인 노래",
                value=self.next_tracks_message,
                inline=False,
            )

        @property
        def image_url(self) -> str:
            if self.music.is_playing:
                return self.music.current_track.artwork
            return DEFAULT_IMG

        @property
        def current_track_message(self) -> str:
            msg: str = ""
            if self.music.current_track is None:
                msg = "재생중인 노래가 없습니다."
                msg += "\n```" f"00:00 {self.dot}{self.thin_line * 20} 00:00" "```"
            else:
                msg = f"[{self.music.current_track.title}]({self.music.current_track.uri})"
                msg += (
                    "\n```"
                    f"{ms_to_str(self.music.current_track.position)} {self.dot}{self.thin_line * 20} {ms_to_str(self.music.current_track.length)}"
                    "```"
                )

            return msg

        @property
        def next_tracks_message(self) -> str:
            page = self.music.current_page
            tracks = self.music.next_tracks[(10 * page) : (10 * (page + 1))]

            nums_emoji = {
                1: "➀",
                2: "➁",
                3: "➂",
                4: "➃",
                5: "➄",
                6: "➅",
                7: "➆",
                8: "➇",
                9: "➈",
                10: "➉",
            }

            return "".join(
                [
                    f"{nums_emoji[idx + 1]}{self.space}[{wrap(track.title)}]({track.uri})\n"
                    for idx, track in enumerate(tracks)
                ]
            ) + "".join(
                [
                    f"{nums_emoji[idx + 1]}{self.space}예약된 노래가 없습니다.\n"
                    for idx in range(len(tracks), 10)
                ]
            )

    class View(ui.View):

        def __init__(self, music: Music):
            super().__init__(timeout=None)
            self.music = music

            components = [
                [
                    MusicUi.Button(
                        (
                            ButtonStyle.green
                            if not self.music.is_paused
                            else ButtonStyle.red
                        ),
                        label="재생" if not self.music.is_paused else "정지",
                        custom_id="pause",
                        row=0,
                    ),
                    MusicUi.Button(
                        ButtonStyle.blurple,
                        label="스킵️",
                        custom_id="skip",
                        row=0,
                    ),
                    MusicUi.Button(
                        ButtonStyle.blurple,
                        label="셔플",
                        custom_id="shuffle",
                        row=0,
                    ),
                    MusicUi.Button(
                        ButtonStyle.grey,
                        label="반복",
                        custom_id="repeat",
                        row=0,
                        disabled=True,
                    ),
                    MusicUi.Button(
                        ButtonStyle.grey,
                        label="도움말",
                        custom_id="help",
                        row=0,
                    ),
                ],
                [
                    MusicUi.Button(
                        ButtonStyle.grey,
                        label="이전",
                        custom_id="prev_page",
                        row=1,
                    ),
                    MusicUi.Button(
                        ButtonStyle.grey,
                        label="다음",
                        custom_id="next_page",
                        row=1,
                    ),
                    MusicUi.Button(
                        (
                            ButtonStyle.blurple
                            if self.music.is_autoplaying
                            else ButtonStyle.grey
                        ),
                        label="자동",
                        custom_id="auto",
                        row=1,
                    ),
                    MusicUi.Button(
                        ButtonStyle.red,
                        label="삭제",
                        custom_id="delete",
                        row=1,
                    ),
                    MusicUi.Button(
                        ButtonStyle.red,
                        label="초기화",
                        custom_id="reset",
                        row=1,
                    ),
                ],
            ]

            for component in components:
                [self.add_item(button) for button in component]

    class Button(ui.Button[View]):

        def __init__(
            self,
            style: ButtonStyle,
            label: str,
            custom_id: str,
            row: int,
            disabled: bool = False,
        ):
            super().__init__(
                style=style,
                label=label,
                custom_id=custom_id,
                row=row,
                disabled=disabled,
            )

        async def callback(self, interaction: Interaction):
            assert self.view is not None

            actions = {
                # First Row
                "pause": self.view.music.pause,
                "skip": self.view.music.skip,
                "shuffle": self.view.music.shuffle,
                "repeat": self.view.music.repeat,
                "help": self.view.music.help,
                # Second Row
                "prev_page": self.view.music.prev_page,
                "next_page": self.view.music.next_page,
                "auto": self.view.music.auto,
                "delete": self.view.music.delete,
                "reset": self.view.music.reset,
            }

            await actions[self.custom_id](interaction)

    @staticmethod
    def make_ui(music: Music) -> tuple[Embed, View]:
        return MusicUi.Embed(music), MusicUi.View(music)
