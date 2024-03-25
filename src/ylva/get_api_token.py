from .config import Config
from .one_password import one_password_get_item, one_password_read


async def get_api_token(config: Config) -> str:
    """
    Retrieve the API authentication token from configuration.
    This allows you to keep API token in your secure vault instead
    of storing it in clear text

    :param config: your current configuration
    :returns: the correctly resolved API token
    """
    if config.api_token is not None:
        api_token: str = config.api_token
    elif config.op_item_id is not None:
        api_token: str = await one_password_get_item(config.op_item_id, "credential")
    elif config.op_item_ref is not None:
        api_token: str = await one_password_read(config.op_item_ref)
    else:
        raise ValueError(
            "No API authentication token is defined: you must set one of the config parameters 'api_token', "
            "'op_item_id', or 'op_item_ref'"
        )

    return api_token
