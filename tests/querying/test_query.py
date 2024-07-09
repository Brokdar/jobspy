"""Test suite for the querying language implementation."""

import pytest

from jobspy.querying.query import (
    ComparisonOperator,
    Condition,
    InvalidOperatorError,
    LogicOperator,
    Query,
    TypeMismatchError,
)
from tests import TestItem


class TestGroupConditions:
    """Test group that checks the condition logic."""

    @pytest.mark.parametrize(
        ["operator", "expected_result"],
        [(ComparisonOperator.EQ, True), (ComparisonOperator.NE, False)],
        ids=["EQ", "NE"],
    )
    def test_evaluate_string_values_with_valid_operators(
        self, operator: ComparisonOperator, expected_result: bool, single_item: TestItem
    ) -> None:
        """Evaluates string fields of an item."""
        condition = Condition("name", operator, single_item.name)
        assert condition.evaluate(single_item) is expected_result

    @pytest.mark.parametrize(
        ["operator", "expected_result"],
        [(ComparisonOperator.EQ, True), (ComparisonOperator.NE, False)],
        ids=["EQ", "NE"],
    )
    def test_evaluate_bool_values_with_valid_operators(
        self, operator: ComparisonOperator, expected_result: bool, single_item: TestItem
    ) -> None:
        """Evaluates bool fields of an item."""
        condition = Condition("active", operator, single_item.active)
        assert condition.evaluate(single_item) is expected_result

    @pytest.mark.parametrize(
        ["operator", "expected_result"],
        [
            (ComparisonOperator.EQ, True),
            (ComparisonOperator.NE, False),
            (ComparisonOperator.LT, False),
            (ComparisonOperator.GT, False),
            (ComparisonOperator.LE, True),
            (ComparisonOperator.GE, True),
        ],
        ids=["EQ", "NE", "LT", "GT", "LE", "GE"],
    )
    def test_evaluate_int_values_with_valid_operators(
        self, operator: ComparisonOperator, expected_result: bool, single_item: TestItem
    ):
        """Evaluates int field of an item."""
        condition = Condition("id", operator, single_item.id)
        assert condition.evaluate(single_item) is expected_result

    @pytest.mark.parametrize(
        ["operator", "expected_result"],
        [
            (ComparisonOperator.EQ, True),
            (ComparisonOperator.NE, False),
            (ComparisonOperator.LT, False),
            (ComparisonOperator.GT, False),
            (ComparisonOperator.LE, True),
            (ComparisonOperator.GE, True),
        ],
        ids=["EQ", "NE", "LT", "GT", "LE", "GE"],
    )
    def test_evaluate_float_values_with_valid_operators(
        self, operator: ComparisonOperator, expected_result: bool, single_item: TestItem
    ):
        """Evaluates float field of an item."""
        condition = Condition("factor", operator, single_item.factor)
        assert condition.evaluate(single_item) is expected_result

    @pytest.mark.parametrize(
        ["operator", "expected_result"],
        [
            (ComparisonOperator.EQ, True),
            (ComparisonOperator.NE, False),
            (ComparisonOperator.LT, False),
            (ComparisonOperator.GT, False),
            (ComparisonOperator.LE, True),
            (ComparisonOperator.GE, True),
        ],
        ids=["EQ", "NE", "LT", "GT", "LE", "GE"],
    )
    def test_evaluate_datetime_values_with_valid_operators(
        self, operator: ComparisonOperator, expected_result: bool, single_item: TestItem
    ):
        """Evaluates datetime field of an item."""
        condition = Condition("created_at", operator, single_item.created_at)
        assert condition.evaluate(single_item) is expected_result

    @pytest.mark.parametrize(
        ["operator", "expected_result"],
        [
            (ComparisonOperator.EQ, True),
            (ComparisonOperator.NE, False),
            (ComparisonOperator.LT, False),
            (ComparisonOperator.GT, False),
            (ComparisonOperator.LE, True),
            (ComparisonOperator.GE, True),
        ],
        ids=["EQ", "NE", "LT", "GT", "LE", "GE"],
    )
    def test_evaluate_timedelta_values_with_valid_operators(
        self, operator: ComparisonOperator, expected_result: bool, single_item: TestItem
    ):
        """Evaluates timedelta field of an item."""
        condition = Condition("duration", operator, single_item.duration)
        assert condition.evaluate(single_item) is expected_result

    @pytest.mark.parametrize(
        "operator",
        [
            operator
            for operator in ComparisonOperator
            if operator not in (ComparisonOperator.EQ, ComparisonOperator.NE)
        ],
    )
    def test_invalid_string_operators_raise_error(
        self, operator: ComparisonOperator, single_item: TestItem
    ) -> None:
        """Invalid string operators raise error."""
        condition = Condition("name", operator, single_item.name)
        with pytest.raises(InvalidOperatorError):
            condition.evaluate(single_item)

    def test_raises_error_on_mismatching_types(self, single_item: TestItem) -> None:
        """Raises error on mismatching types."""
        condition = Condition("name", ComparisonOperator.EQ, 1)
        with pytest.raises(TypeMismatchError):
            condition.evaluate(single_item)


class TestGroupQuery:
    """Test group that tests the query logic."""

    @pytest.mark.parametrize(
        ["name", "id", "logic_operator", "expected_result"],
        [
            ("Alice", 1, LogicOperator.AND, True),
            ("Bob", 1, LogicOperator.AND, False),
            ("Alice", 2, LogicOperator.OR, True),
            ("Bob", 1, LogicOperator.OR, True),
            ("Bob", 2, LogicOperator.OR, False),
        ],
        ids=[
            "name = Alice AND id = 1",
            "name = Bob AND id = 1",
            "name = Alice or id = 2",
            "name = Bob or id = 1",
            "name = Bob or id = 2",
        ],
    )
    def test_combines_conditions_logically(
        self,
        name: str,
        id: int,
        logic_operator: LogicOperator,
        expected_result: bool,
        single_item: TestItem,
    ) -> None:
        """Combines conditions logically."""
        query = Query(
            [
                Condition("name", ComparisonOperator.EQ, name),
                Condition("id", ComparisonOperator.EQ, id),
            ],
            logic_operator,
        )

        assert query.evaluate(single_item) is expected_result

    def test_complex_query(self, single_item: TestItem) -> None:
        """Tests complex query logic."""
        # (name = Alice OR id = 1) AND factor <= 2.0
        query = Query(
            [
                Query(
                    [
                        Condition("name", ComparisonOperator.EQ, "Alice"),
                        Condition("id", ComparisonOperator.EQ, 1),
                    ],
                    LogicOperator.OR,
                ),
                Condition("factor", ComparisonOperator.GE, 2.0),
            ],
            LogicOperator.AND,
        )

        assert query.evaluate(single_item) is True
