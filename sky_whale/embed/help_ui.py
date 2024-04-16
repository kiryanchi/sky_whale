from discord import Embed

from setting import DEFAULT_COLOR


class HelpUi:

    class Embed(Embed):
        default = "[0m"
        blue = "[1;34m"
        sky = "[1;36m"
        red = "[1;35m"
        link = "https://youtu.be/T0uFmC2hTKc"
        example_name = "야! 비! 당장 그쳐 뚝! (Remix) 1시간"

        def __init__(self):
            super().__init__(
                title="🐳 하늘 고래는 노래쟁이야",
                color=DEFAULT_COLOR,
            )

            self.set_author(
                name="자세한 사용법은 여기를 클릭하면 확인할 수 있습니다.",
                url="https://discord.gg/T92wcQuznv",
            )
            self.add_field(
                name="하늘고래가 고장났을 때",
                value=f"```ansi\n{self.blue}/고래 초기화{self.default}``` 명령어로 고래를 **초기화**하세요!",
                inline=False,
            )
            self.add_field(
                name="음악 재생",
                value=f"""음악 재생에는 3가지 방법이 있습니다.
                **유튜브 링크를 재생**
                유튜브 링크로 바로 노래를 재생합니다.
                ```ansi\n1. {self.blue}/고래 재생 [유튜브 링크]{self.default} 명령어 사용\n2. {self.sky}음악 채널에 [유튜브 링크]{self.default} 전송\nex) /고래 재생 {self.link}\n```
                **제목을 검색**
                제목으로 10개의 유튜브를 검색합니다.
                ```ansi\n1. {self.blue}/고래 재생 [제목]{self.default} 명령어 사용\n2. {self.sky}음악 채널에 [제목]{self.default} 전송\nex) /고래 재생 {self.example_name}```
                **제목으로 바로 재생**
                제목 앞에 !(느낌표)를 붙여서 바로 재생합니다.
                ```ansi\n1. {self.blue}/고래 재생 [!제목]{self.default} 명령어 사용\n2. {self.sky}음악 채널에 [!제목]{self.default} 전송\nex) /고래 재생 !{self.example_name}```
                """,
                inline=True,
            )
            self.add_field(
                name="플레이어 조작",
                value=f"""음악을 재생하며 여러 편의기능을 제공합니다.
                **일시정지/재생**
                노래를 일시정지 혹은 다시 재생합니다.
                ```ansi\n1. {self.blue}/고래 정지{self.default} 명령어 사용\n2. {self.sky}음악 채널에 재생(정지){self.default} 버튼 클릭\n```
                **스킵**
                노래 한 곡을 스킵합니다.
                ```ansi\n1. {self.blue}/고래 스킵{self.default} 명령어 사용\n2. {self.sky}음악 채널에서 스킵{self.default} 버튼 클릭\n```
                **셔플**
                재생목록을 섞습니다.
                ```ansi\n1. {self.blue}/고래 셔플{self.default} 명령어 사용\n2. {self.sky}음악 채널에서 셔플{self.default} 버튼 클릭\n```
                **한곡 반복**
                현재 재생중인 노래를 반복재생합니다.
                ```ansi\n1. {self.blue}/고래 반복{self.default} 명령어 사용\n2. {self.sky}음악 채널에서 반복{self.default} 버튼 클릭\n```
                """,
                inline=True,
            )

    @staticmethod
    def make_ui() -> Embed:
        return HelpUi.Embed()
