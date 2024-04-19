from __future__ import annotations

import os
from typing import TYPE_CHECKING

from supabase._async.client import create_client

from sky_whale.db.music_channel import MusicChannel

if TYPE_CHECKING:
    from supabase._async.client import AsyncClient

    from sky_whale.dto.music_channel_dto import MusicChannelDto


class SupaBaseConnector:
    __instance: SupaBaseConnector | None = None
    supabase: AsyncClient
    url: str
    key: str

    def __init__(self):
        self.url: str = os.environ.get("SUPABASE_URL")
        self.key: str = os.environ.get("SUPABASE_KEY")

    async def insert(self, guild_id: int, channel_id: int) -> MusicChannel | None:
        if api_response := (
            await self.supabase.table("music_channel")
            .insert({"guild_id": guild_id, "channel_id": channel_id})
            .execute()
        ):
            datas: list[MusicChannelDto] = api_response.data
            return MusicChannel.from_dto(datas[0])

    async def fetch(self, guild_id: int) -> MusicChannel | None:
        if api_response := (
            await self.supabase.table("music_channel")
            .select("*")
            .eq("guild_id", guild_id)
            .execute()
        ):
            datas: list[MusicChannelDto] = api_response.data
            return MusicChannel.from_dto(datas[0])

    async def fetch_all(self) -> list[MusicChannel]:
        if api_response := (
            await self.supabase.table("music_channel").select("*").execute()
        ):
            datas: list[MusicChannelDto] = api_response.data
            return [MusicChannel.from_dto(data) for data in datas]

    async def update(self, guild_id: int, channel_id: int) -> MusicChannel | None:
        if api_response := (
            await self.supabase.table("music_channel")
            .update({"channel_id": channel_id})
            .eq("guild_id", guild_id)
            .execute()
        ):
            datas: list[MusicChannelDto] = api_response.data
            return MusicChannel.from_dto(datas[0])

    async def delete(self, guild_id: int) -> None:
        (
            await self.supabase.table("music_channel")
            .delete()
            .eq("guild_id", guild_id)
            .execute()
        )

    async def _initialize(self):
        self.supabase = await create_client(self.url, self.key)

    @classmethod
    async def get_instance(cls) -> SupaBaseConnector:
        if cls.__instance is None:
            cls.__instance = SupaBaseConnector()
            await cls.__instance._initialize()
        return cls.__instance
