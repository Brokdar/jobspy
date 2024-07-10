"""Test suite for testing the parsing of query strings."""

import pytest

from jobspy.querying.parser import QueryParser
from jobspy.querying.query import ComparisonOperator, Condition, LogicOperator, Query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        (
            "id = 1 AND name = Alice",
            Query(
                [
                    Condition("id", ComparisonOperator.EQ, 1),
                    Condition("name", ComparisonOperator.EQ, "Alice"),
                ],
                LogicOperator.AND,
            ),
        ),
        (
            "id = 1 and name = Alice",
            Query(
                [
                    Condition("id", ComparisonOperator.EQ, 1),
                    Condition("name", ComparisonOperator.EQ, "Alice"),
                ],
                LogicOperator.AND,
            ),
        ),
        (
            "id = 1 OR name = Alice",
            Query(
                [
                    Condition("id", ComparisonOperator.EQ, 1),
                    Condition("name", ComparisonOperator.EQ, "Alice"),
                ],
                LogicOperator.OR,
            ),
        ),
        (
            "id = 1 or name = Alice",
            Query(
                [
                    Condition("id", ComparisonOperator.EQ, 1),
                    Condition("name", ComparisonOperator.EQ, "Alice"),
                ],
                LogicOperator.OR,
            ),
        ),
        (
            "id = 1 AND name = Alice AND active = True",
            Query(
                [
                    Condition("id", ComparisonOperator.EQ, 1),
                    Condition("name", ComparisonOperator.EQ, "Alice"),
                    Condition("active", ComparisonOperator.EQ, True),
                ],
                LogicOperator.AND,
            ),
        ),
        (
            "id = 1 OR name = Alice OR active = True",
            Query(
                [
                    Condition("id", ComparisonOperator.EQ, 1),
                    Condition("name", ComparisonOperator.EQ, "Alice"),
                    Condition("active", ComparisonOperator.EQ, True),
                ],
                LogicOperator.OR,
            ),
        ),
    ],
    ids=[
        "id = 1 AND name = Alice",
        "id = 1 and name = Alice",
        "id = 1 OR name = Alice",
        "id = 1 or name = Alice",
        "id = 1 AND name = Alice AND active = True",
        "id = 1 OR name = Alice OR active = True",
    ],
)
def test_parses_multiple_condition(query_str: str, expected_query: Query) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query


@pytest.mark.parametrize(
    ["query_str", "expected_query"],
    [
        (
            "id = 1 OR name = Alice AND active = True",
            Query(
                [
                    Condition("id", ComparisonOperator.EQ, 1),
                    Query(
                        [
                            Condition("name", ComparisonOperator.EQ, "Alice"),
                            Condition("active", ComparisonOperator.EQ, True),
                        ],
                        LogicOperator.AND,
                    ),
                ],
                LogicOperator.OR,
            ),
        ),
        (
            "name = Alice AND active = True OR id = 1",
            Query(
                [
                    Query(
                        [
                            Condition("name", ComparisonOperator.EQ, "Alice"),
                            Condition("active", ComparisonOperator.EQ, True),
                        ],
                        LogicOperator.AND,
                    ),
                    Condition("id", ComparisonOperator.EQ, 1),
                ],
                LogicOperator.OR,
            ),
        ),
    ],
    ids=[
        "id = 1 OR name = Alice AND active = True",
        "name = Alice AND active = True OR id = 1",
    ],
)
def test_parses_dominant_operator_first(query_str: str, expected_query: Query) -> None:
    """Tests the parsing of a single condition."""
    parser = QueryParser()
    result = parser.parse(query_str)
    assert result == expected_query
