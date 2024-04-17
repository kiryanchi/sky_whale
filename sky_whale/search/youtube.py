from __future__ import annotations

from youtubesearchpython.__future__ import VideosSearch

from setting import NUM_OF_SEARCH
from sky_whale.type.types import VideosSearchResult


class Video:

    def __init__(self, title: str, uploader: str, duration: str, link: str) -> None:
        logger.debug(
            f"Title: {title}, Uploader: {uploader}, Duration: {duration}, Link: {link}"
        )
        if not (title and uploader and duration and link):
            raise ValueError("Invalid value")
        self.title = title
        self.uploader = uploader
        self.duration = duration
        self.link = link

    def __repr__(self) -> str:
        return f"YoutubeSearchResult(title={self.title}, uploader={self.uploader}, duration={self.duration}, link={self.link})"

    def __str__(self) -> str:
        return (
            f"Title: {self.title}, Uploader: {self.uploader}, Duration: {self.duration}"
        )


async def search_from_youtube(query: str) -> list[Video]:
    videos: VideosSearchResult | None
    if videos := (await VideosSearch(query=query, limit=NUM_OF_SEARCH).next()).get(
        "result", None
    ):
        return [
            Video(
                title=video.get("title", None),
                uploader=video.get("channel", {}).get("name", None),
                duration=video.get("duration", None),
                link=video.get("link", None),
            )
            for video in videos
        ]
    else:
        raise ValueError("검색 결과가 없습니다.")
