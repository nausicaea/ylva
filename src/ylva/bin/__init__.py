import asyncio
import functools
import sys
from pathlib import Path
from typing import Callable, Coroutine

from appdirs import AppDirs

APP_IDENTIFIER = "net.nausicaea.ylva"
APP_AUTHOR = "nausicaea"
YML_SUFFIX = ".yml"
YML_SUFFIXES = (YML_SUFFIX, ".yaml")

APPDIRS = AppDirs(APP_IDENTIFIER, APP_AUTHOR)
CONFIG_DIR = Path(APPDIRS.user_config_dir)
DEFAULT_CONFIG_FILE = CONFIG_DIR.joinpath(f"config{YML_SUFFIX}")


def start(coro: Callable[[], Coroutine]) -> Callable[[], None]:
    @functools.wraps(coro)
    def wrapper() -> None:
        if sys.version_info >= (3, 7):
            asyncio.run(coro())
        else:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(coro())
            if not loop.is_closed():
                loop.close()

    return wrapper
