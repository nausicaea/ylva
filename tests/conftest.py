import asyncio
import asyncio.subprocess
from asyncio.events import AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from reidun.auth_method import BearerAuth
from reidun.client import ApiClient

from ylva.one_password import one_password_get_item


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def ynab_api_token_id() -> str:
    return "2vwn7fnsrhyzdb4w37dlmnrt4y"


@pytest_asyncio.fixture(scope="session")
async def ynab_api_url(ynab_api_token_id: str) -> str:
    host_name: str = await one_password_get_item(ynab_api_token_id, "hostname")
    return f"https://{host_name}/"


@pytest_asyncio.fixture(scope="session")
async def ynab_api_token(ynab_api_token_id: str) -> str:
    return await one_password_get_item(ynab_api_token_id, "credential")


@pytest_asyncio.fixture(scope="session")
async def ynab_default_budget(ynab_api_token_id: str) -> str:
    return await one_password_get_item(ynab_api_token_id, "default budget")


@pytest_asyncio.fixture(scope="session")
async def ynab_api_client(
    ynab_api_url: str, ynab_api_token: str
) -> AsyncGenerator[ApiClient, None]:
    async with ApiClient(ynab_api_url, auth=BearerAuth(ynab_api_token)) as client:
        yield client
