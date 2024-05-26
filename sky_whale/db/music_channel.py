from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    pass


class Base(DeclarativeBase):
    pass


class MusicChannel(Base):
    __tablename__ = "music_channel"
    guild_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer)
