import asyncio


async def one_password_get_item(item_id: str, field_name: str) -> str:
    """
    Retrieve an item from the One Password vault

    :param item_id: the vault ID
    :param field_name: the field within the vault item to retrieve
    :return: the value of the vault item
    :raise ValueError: if retrieval failed due to non-zero subprocess returncode
    """
    proc = await asyncio.subprocess.create_subprocess_exec(
        "op",
        "item",
        "get",
        item_id,
        "--fields",
        f"label={field_name}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise ValueError(stderr.decode("utf-8"))

    return stdout.strip().decode("utf-8")


async def one_password_read(item_ref: str) -> str:
    """
    Retrieve a field from the One Password vault

    :param item_ref: the unique OnePassword reference to the field
    :return: the value of the vault item
    :raise ValueError: if retrieval failed due to non-zero subprocess returncode
    """
    proc = await asyncio.subprocess.create_subprocess_exec(
        "op",
        "read",
        item_ref,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise ValueError(stderr.decode("utf-8"))

    return stdout.strip().decode("utf-8")
