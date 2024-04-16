from __future__ import annotations

from typing import Optional

from sqlalchemy import Column, Integer, select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import UnmappedInstanceError

from sky_whale.db.base import Base, async_session


class MusicChannel(Base):
    __tablename__ = "music_channel"
    guild_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)

    def __repr__(self) -> str:
        return f"MusicChannel(guild_id={self.guild_id}, channel_id={self.channel_id})"

    def __str__(self) -> str:
        return f"MusicChanel(guild_id={self.guild_id}, channel_id={self.channel_id})"

    @staticmethod
    async def add(guild_id: int, channel_id: int):
        async with async_session() as session:
            try:
                session.add(
                    MusicChannel(
                        guild_id=guild_id,
                        channel_id=channel_id,
                    )
                )
                await session.commit()

                return True
            except IntegrityError:
                return False

    @staticmethod
    async def get(guild_id: int) -> Optional[MusicChannel]:
        async with async_session() as session:
            return (
                (
                    await session.execute(
                        select(MusicChannel).where(MusicChannel.guild_id == guild_id)
                    )
                )
                .scalars()
                .first()
            )

    @staticmethod
    async def get_all() -> list[MusicChannel]:
        async with async_session() as session:
            return (await session.execute(select(MusicChannel))).scalars().all()

    @staticmethod
    async def update(guild_id: int, channel_id: int) -> bool:
        async with async_session() as session:
            try:
                await session.execute(
                    update(MusicChannel)
                    .where(MusicChannel.guild_id == guild_id)
                    .values(channel_id=channel_id)
                )
                await session.commit()

                return True
            except UnmappedInstanceError:
                return False

    @staticmethod
    async def delete(guild_id: int) -> bool:
        async with async_session() as session:
            try:
                await session.execute(
                    delete(MusicChannel).where(MusicChannel.guild_id == guild_id)
                )
                await session.commit()

                return True
            except UnmappedInstanceError:
                return False

    @staticmethod
    async def flush() -> list[MusicChannel]:
        async with async_session() as session:
            await session.execute(delete(MusicChannel))
            await session.commit()

            return list((await session.execute(select(MusicChannel))).scalars().all())
