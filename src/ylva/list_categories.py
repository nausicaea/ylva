from typing import cast

from reidun.client import ApiClient

from .ynab.categories.list import CategoriesResponse, ListCategories
from .ynab.model.category import Category


async def list_categories(client: ApiClient, budget_id: str) -> list[Category]:
    """
    Retrieve a list of categories from YNAB

    :param client: the YNAB REST API client
    :param budget_id: the budget reference to retrieve categories from
    :raise ValueError: when there are no categories
    """
    categories, _ = await client.get(ListCategories(budget_id))
    if categories is not None:
        cats: CategoriesResponse = cast(CategoriesResponse, categories)
        if len(cats.data.category_groups) == 0 or all(
            len(cg.categories) == 0 for cg in cats.data.category_groups
        ):
            raise ValueError(f"Budget {budget_id} has no categories")
        return [c for cg in cats.data.category_groups for c in cg.categories]

    else:
        raise ValueError(f"Budget {budget_id} has no categories")
