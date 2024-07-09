"""Test suite for testing the parsing of query strings."""

from datetime import datetime, timedelta

import pytest

from jobspy.querying.parser import QueryParser
from jobspy.querying.query import ComparisonOperator, Condition, Query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        ("id = 100", Query([Condition("id", ComparisonOperator.EQ, 100)])),
        ("id != 100", Query([Condition("id", ComparisonOperator.NE, 100)])),
        ("id < 100", Query([Condition("id", ComparisonOperator.LT, 100)])),
        ("id > 100", Query([Condition("id", ComparisonOperator.GT, 100)])),
        ("id <= 100", Query([Condition("id", ComparisonOperator.LE, 100)])),
        ("id >= 100", Query([Condition("id", ComparisonOperator.GE, 100)])),
    ],
    ids=["id = 100", "id != 100", "id < 100", "id > 100", "id <= 100", "id >= 100"],
)
def test_parses_single_condition(query_str: str, expected_query: Query) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)

    assert str(result) == str(expected_query)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        ("id=100", Query([Condition("id", ComparisonOperator.EQ, 100)])),
        ("id!=100", Query([Condition("id", ComparisonOperator.NE, 100)])),
        ("id<100", Query([Condition("id", ComparisonOperator.LT, 100)])),
        ("id>100", Query([Condition("id", ComparisonOperator.GT, 100)])),
        ("id<=100", Query([Condition("id", ComparisonOperator.LE, 100)])),
        ("id>=100", Query([Condition("id", ComparisonOperator.GE, 100)])),
    ],
    ids=["id=100", "id!=100", "id<100", "id>100", "id<=100", "id>=100"],
)
def test_parses_single_condition_without_spaces(
    query_str: str, expected_query: Query
) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)

    assert str(result) == str(expected_query)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        ("name = Alice", Query([Condition("name", ComparisonOperator.EQ, "Alice")])),
        ("name = 'Alice'", Query([Condition("name", ComparisonOperator.EQ, "Alice")])),
        ('name = "Alice"', Query([Condition("name", ComparisonOperator.EQ, "Alice")])),
    ],
    ids=["name = Alice", "name = 'Alice'", 'name = "Alice"'],
)
def test_parses_single_condition_of_type_string(
    query_str: str, expected_query: Query
) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        ("id = 100", Query([Condition("id", ComparisonOperator.EQ, 100)])),
        ("id = -100", Query([Condition("id", ComparisonOperator.EQ, -100)])),
        ("id = 0", Query([Condition("id", ComparisonOperator.EQ, 0)])),
    ],
    ids=["id = 100", "id = -100", "id = 0"],
)
def test_parses_single_condition_of_type_int(
    query_str: str, expected_query: Query
) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        ("active = True", Query([Condition("active", ComparisonOperator.EQ, True)])),
        ("active = true", Query([Condition("active", ComparisonOperator.EQ, True)])),
        ("active = False", Query([Condition("active", ComparisonOperator.EQ, False)])),
        ("active = false", Query([Condition("active", ComparisonOperator.EQ, False)])),
    ],
    ids=["active = True", "active = true", "active = False", "active = false"],
)
def test_parses_single_condition_of_type_bool(
    query_str: str, expected_query: Query
) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        ("factor = 100.0", Query([Condition("factor", ComparisonOperator.EQ, 100.0)])),
        (
            "factor = -100.0",
            Query([Condition("factor", ComparisonOperator.EQ, -100.0)]),
        ),
        ("factor = 0.0", Query([Condition("factor", ComparisonOperator.EQ, 0.0)])),
    ],
    ids=["factor = 100.0", "factor = -100.0", "factor = 0.0"],
)
def test_parses_single_condition_of_type_float(
    query_str: str, expected_query: Query
) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        (
            "created_at = 2024-07-01",
            Query(
                [Condition("created_at", ComparisonOperator.EQ, datetime(2024, 7, 1))]
            ),
        ),
        (
            "created_at = 2024-07-01 8:00",
            Query(
                [
                    Condition(
                        "created_at", ComparisonOperator.EQ, datetime(2024, 7, 1, 8, 0)
                    )
                ]
            ),
        ),
        (
            "created_at = 2024-07-01 12:30:45",
            Query(
                [
                    Condition(
                        "created_at",
                        ComparisonOperator.EQ,
                        datetime(2024, 7, 1, 12, 30, 45),
                    )
                ]
            ),
        ),
        (
            "created_at = 24-07-01",
            Query(
                [Condition("created_at", ComparisonOperator.EQ, datetime(2024, 7, 1))]
            ),
        ),
        (
            "created_at = 24-07-01 8:00",
            Query(
                [
                    Condition(
                        "created_at", ComparisonOperator.EQ, datetime(2024, 7, 1, 8, 0)
                    )
                ]
            ),
        ),
        (
            "created_at = 24-07-01 12:30:45",
            Query(
                [
                    Condition(
                        "created_at",
                        ComparisonOperator.EQ,
                        datetime(2024, 7, 1, 12, 30, 45),
                    )
                ]
            ),
        ),
    ],
    ids=[
        "created_at = 2024-07-01",
        "created_at = 2024-07-01 8:00",
        "created_at = 2024-07-01 12:30:45",
        "created_at = 24-07-01",
        "created_at = 24-07-01 8:00",
        "created_at = 24-07-01 12:30:45",
    ],
)
def test_parses_single_condition_of_type_datetime(
    query_str: str, expected_query: Query
) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        (
            "duration = 8:00",
            Query([Condition("duration", ComparisonOperator.EQ, timedelta(hours=8))]),
        ),
        (
            "duration = 12:30:45",
            Query(
                [
                    Condition(
                        "duration",
                        ComparisonOperator.EQ,
                        timedelta(hours=12, minutes=30, seconds=45),
                    )
                ]
            ),
        ),
        (
            "duration = 0:30:15",
            Query(
                [
                    Condition(
                        "duration",
                        ComparisonOperator.EQ,
                        timedelta(minutes=30, seconds=15),
                    )
                ]
            ),
        ),
    ],
    ids=["duration = 8:00", "duration = 12:30:45", "duration = 0:30:15"],
)
def test_parses_single_condition_of_type_timedelta(
    query_str: str, expected_query: Query
) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query
