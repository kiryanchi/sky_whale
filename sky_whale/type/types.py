from typing import TypedDict


class Channel(TypedDict):
    name: str


class VideosSearchResult(TypedDict):
    title: str
    channel: Channel
    duration: str
    link: str
