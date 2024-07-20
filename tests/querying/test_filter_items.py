from datetime import datetime, timedelta

import pytest

from jobspy.querying import filter_items
from jobspy.querying.parser import QueryParser
from tests import TestItem

items = [
    TestItem(
        id=1,
        name="Alice",
        active=True,
        factor=100.0,
        created_at=datetime(2024, 6, 1, 18, 30, 0),
        duration=timedelta(hours=1),
    ),
    TestItem(
        id=2,
        name="Bob",
        active=False,
        factor=1.23,
        created_at=datetime(2024, 6, 2, 18, 30, 0),
        duration=timedelta(hours=1, minutes=30),
    ),
    TestItem(
        id=3,
        name="Charlie",
        active=True,
        factor=-2.45,
        created_at=datetime(2024, 6, 3, 8, 30, 0),
        duration=timedelta(minutes=45),
    ),
    TestItem(
        id=4,
        name="Doris",
        active=False,
        factor=5.8,
        created_at=datetime(2024, 7, 1, 6, 30, 0),
        duration=timedelta(hours=1),
    ),
]


@pytest.mark.parametrize(
    ["query_str", "ids"],
    [
        ("active=True", [1, 3]),
        ("active=True AND factor>=0.0", [1]),
        ("created_at <= 2024-06-03 OR duration < 1:00:00", [1, 2, 3]),
        ("duration > 1:00:00", [2]),
    ],
)
def test_filter_items(query_str: str, ids: list[int]) -> None:
    """Test filtering of items."""
    query = QueryParser().parse(query_str)
    result = filter_items(query, items)
    assert ids == [item.id for item in result]
