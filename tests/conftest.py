import asyncio
import asyncio.subprocess
from asyncio.events import AbstractEventLoop
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from reidun.auth_method import BearerAuth
from reidun.client import ApiClient

from ylva.category_lut import CategoryLut
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


@pytest.fixture
def category_lut() -> CategoryLut:
    return CategoryLut(
        payee_id_to_category_id={},
        monthweek_to_category_id={
            0: "313fd8eb-5d59-41ea-9103-ce352113a41c",
            1: "313fd8eb-5d59-41ea-9103-ce352113a41c",
            2: "7362c8ac-e69b-482a-9b7f-8d05c3b61838",
            3: "4f733120-d26a-42d5-b03d-a3bc08d6a113",
            4: "474e09b8-dee9-4bf5-b31c-ab6c01d3a031",
        },
    )
