from __future__ import annotations

import logging
import logging.handlers
import os.path
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import TYPE_CHECKING

from discord import Interaction
from rich.logging import RichHandler

if TYPE_CHECKING:
    from discord import Message

LOG_PATH = "./log/botLog.log"
RICH_FORMAT = "[%(filename)s:%(lineno)s] >> %(message)s"
FILE_HANDLER_FORMAT = "[%(asctime)s]\\t%(levelname)s\\t[%(filename)s:%(funcName)s:%(lineno)s]\\t>> %(message)s"

if not os.path.exists("./log/"):
    os.makedirs("./log/")


def set_logger() -> logging.Logger:
    def handle_exception(exc_type, exc_value, exc_traceback):
        logger = logging.getLogger("rich")

        logger.exception(
            "Unexpected exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    logging.basicConfig(
        level="DEBUG",
        format=RICH_FORMAT,
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    logger = logging.getLogger("rich")
    sys.excepthook = handle_exception

    file_handler = TimedRotatingFileHandler(LOG_PATH, when="midnight", interval=1)
    file_handler.setLevel("DEBUG")
    file_handler.suffix = "%Y%m%d"
    file_handler.setFormatter(logging.Formatter(FILE_HANDLER_FORMAT))
    logger.addHandler(file_handler)

    return logger


class Trace:

    @staticmethod
    def command(_logger: logging.Logger):
        def wrapper(func):
            async def decorator(*args, **kwargs):
                _ctx: Interaction | Message = (
                    kwargs["ctx"] if kwargs.get("ctx", None) else kwargs["interaction"]
                )
                _member = _ctx.user if isinstance(_ctx, Interaction) else _ctx.author

                _msg = f"[명령어] 길드({_ctx.guild.name}, {_ctx.guild.id}): '{_member.name}', '{func.__name__}' 사용"
                if func.__name__ == "play":
                    _msg += f", '{kwargs['query']}' 검색"

                _logger.info(msg=_msg)
                return await func(*args, **kwargs)

            return decorator

        return wrapper


logger = set_logger()
