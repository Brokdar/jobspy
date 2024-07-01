"""Test suite for the querying language implementation."""

from datetime import datetime, timedelta
import pytest

from jobspy.querying import (
    ComparisonOperator,
    Condition,
    InvalidOperatorError,
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
        condition = Condition("name", operator, "Alice")
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
        condition = Condition("active", operator, True)
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
        condition = Condition("id", operator, 1)
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
        condition = Condition("factor", operator, 100.0)
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
        condition = Condition("created_at", operator, datetime(2024, 6, 1, 18, 30, 0))
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
        condition = Condition("duration ", operator, timedelta(hours=1))
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
        condition = Condition("name", operator, "Alice")
        with pytest.raises(InvalidOperatorError):
            condition.evaluate(single_item)

    def test_raises_error_on_mismatching_types(self, single_item: TestItem) -> None:
        """Raises error on mismatching types."""
        condition = Condition("name", ComparisonOperator.EQ, 1)
        with pytest.raises(TypeError):
            condition.evaluate(single_item)
