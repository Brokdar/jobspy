from datetime import datetime, timedelta

import pytest

from tests import TestItem


@pytest.fixture(scope="module")
def single_item() -> TestItem:
    """Returns a single test item."""
    return TestItem(
        id=1,
        name="Alice",
        active=True,
        factor=100.0,
        created_at=datetime(2024, 6, 1, 18, 30, 0),
        duration=timedelta(hours=1),
    )
