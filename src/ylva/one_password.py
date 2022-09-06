import asyncio


async def one_password_get_item(item_id: str, field_name: str) -> str:
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
    stdout, _ = await proc.communicate()
    return stdout.strip().decode("utf-8")
