"""Implements a flexible querying language for filtering lists of data based on various conditions and operators."""

from typing import Generator, TypeVar

from pydantic import BaseModel

from jobspy.querying.query import Query

T = TypeVar("T", bound=BaseModel)


def filter_items(query: Query, items: list[T]) -> Generator[T, None, None]:
    """Filter a list of items based on a query.

    Args:
        query (Query): the query to filter by.
        items (list[T]): the list of items to filter.

    Returns:
        Generator[T]: A filtered list of items that match the query.
    """
    return (item for item in items if query.evaluate(item))
