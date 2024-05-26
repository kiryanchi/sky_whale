from __future__ import annotations

from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sky_whale.db.music_channel import MusicChannel
from sky_whale.util.log import Trace, logger


class SQLiteConnector:
    __instance: SQLiteConnector | None = None

    def __init__(self):
        self.engine = create_engine("sqlite:///sky_whale.db", echo=True)

        logger.debug("[클래스] SQLiteConnector 생성")

    @Trace.trace(logger)
    def insert(self, music_channel: MusicChannel):
        with Session(self.engine) as session:
            session.add(music_channel)
            session.commit()

    @Trace.trace(logger)
    def fetch(self, guild_id: int) -> MusicChannel | None:
        with Session(self.engine) as session:
            return session.get(MusicChannel, guild_id)

    @Trace.trace(logger)
    def fetch_all(self) -> list[Type[MusicChannel]]:
        with Session(self.engine) as session:
            return session.query(MusicChannel).all()

    @Trace.trace(logger)
    def update(self, guild_id: int, channel_id: int):
        with Session(self.engine) as session:
            if music_channel := session.get(MusicChannel, guild_id):
                music_channel.channel_id = channel_id
                session.commit()

    @Trace.trace(logger)
    def delete(self, guild_id: int):
        with Session(self.engine) as session:
            if music_channel := session.get(MusicChannel, guild_id):
                session.delete(music_channel)
                session.commit()

    @classmethod
    def get_instance(cls) -> SQLiteConnector:
        if cls.__instance is None:
            cls.__instance = SQLiteConnector()
        return cls.__instance
