import asyncio
import functools
from typing import Callable, Coroutine
import sys


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
