import asyncio
import asyncio.subprocess
from asyncio.events import AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from reidun.auth_method import BearerAuth
from reidun.client import ApiClient


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def ynab_api_url() -> str:
    return "https://api.youneedabudget.com"


@pytest_asyncio.fixture(scope="session")
async def ynab_personal_api_token(event_loop: AbstractEventLoop) -> str:
    proc = await asyncio.subprocess.create_subprocess_exec(
        "op",
        "item",
        "get",
        "2vwn7fnsrhyzdb4w37dlmnrt4y",
        "--fields",
        "label=credential",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await proc.communicate()

    return stdout.strip().decode("utf-8")


@pytest_asyncio.fixture(scope="session")
async def ynab_api_client(
    ynab_api_url: str, ynab_personal_api_token: str
) -> AsyncGenerator[ApiClient, None]:
    async with ApiClient(
        ynab_api_url, auth=BearerAuth(ynab_personal_api_token)
    ) as client:
        yield client
