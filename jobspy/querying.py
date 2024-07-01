"""Implements a flexible querying language for filtering lists of data based on various conditions and operators."""

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Callable, Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LogicOperator(StrEnum):
    """Enum representing logical operators for combining query conditions."""

    AND = "AND"
    OR = "OR"


class ComparisonOperator(StrEnum):
    """Enum representing comparison operators for query conditions."""

    EQ = "="
    NE = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="


VALID_OPERATOR_MAP: dict[type, list[ComparisonOperator]] = {
    str: [ComparisonOperator.EQ, ComparisonOperator.NE],
    bool: [ComparisonOperator.EQ, ComparisonOperator.NE],
    int: [
        ComparisonOperator.EQ,
        ComparisonOperator.NE,
        ComparisonOperator.LT,
        ComparisonOperator.GT,
        ComparisonOperator.LE,
        ComparisonOperator.GE,
    ],
    float: [
        ComparisonOperator.EQ,
        ComparisonOperator.NE,
        ComparisonOperator.LT,
        ComparisonOperator.GT,
        ComparisonOperator.LE,
        ComparisonOperator.GE,
    ],
    datetime: [
        ComparisonOperator.EQ,
        ComparisonOperator.NE,
        ComparisonOperator.LT,
        ComparisonOperator.GT,
        ComparisonOperator.LE,
        ComparisonOperator.GE,
    ],
    timedelta: [
        ComparisonOperator.EQ,
        ComparisonOperator.NE,
        ComparisonOperator.LT,
        ComparisonOperator.GT,
        ComparisonOperator.LE,
        ComparisonOperator.GE,
    ],
}

OPERATOR_FUNCTION_MAP: dict[ComparisonOperator, Callable[[Any, Any], bool]] = {
    ComparisonOperator.EQ: lambda x, y: x == y,
    ComparisonOperator.NE: lambda x, y: x != y,
    ComparisonOperator.LT: lambda x, y: x < y,
    ComparisonOperator.GT: lambda x, y: x > y,
    ComparisonOperator.LE: lambda x, y: x <= y,
    ComparisonOperator.GE: lambda x, y: x >= y,
}


class InvalidOperatorError(Exception):
    """Raises on invalid operator usage."""

    def __init__(
        self, field_name: str, field_type: type, operator: ComparisonOperator
    ) -> None:
        """Initializes an invalid operator error."""
        self.field_name = field_name
        self.field_type = field_type
        self.operator = operator

        super().__init__(
            f"Invalid operator '{operator}' for field '{field_name}' of type '{field_type}'. "
            f"Allowed operators: {', '.join(VALID_OPERATOR_MAP[field_type])}"
        )


class Queryable(Protocol):
    """Protocol defining the interface for objects that can be evaluated against a BaseModel item."""

    def evaluate(self, item: BaseModel) -> bool:
        """Evaluates the queryable against a BaseModel item."""


class Condition(Queryable):
    """Represents a single condition in a query."""

    def __init__(self, field: str, operator: ComparisonOperator, value: Any) -> None:
        """Initializes a condition.

        Args:
            field (str): the field to compare.
            operator (ComparisonOperator): the comparison operator.
            value (Any): the value to compare against.
        """
        self.field = field
        self.operator = operator
        self.value = value

    def __str__(self) -> str:
        """Returns a string representation of the condition."""
        return f"{self.field} {self.operator} {self.value}"

    def evaluate(self, item: BaseModel) -> bool:
        """Evaluate the condition against a BaseModel item.

        Args:
            item (BaseModel): the item to evaluate against.

        Returns:
            bool: True if the query is met, False otherwise.
        """
        item_value = getattr(item, self.field, None)
        if item_value is None:
            return False

        item_type = type(item_value)
        if not isinstance(self.value, item_type):
            raise TypeError(
                f"Field value type doesn't match value type: {item_type} != {type(self.value)}"
            )

        if self.operator not in VALID_OPERATOR_MAP[item_type]:
            raise InvalidOperatorError(self.field, item_type, self.operator)

        return OPERATOR_FUNCTION_MAP[self.operator](item_value, self.value)


class Query(Queryable):
    """Represents a complex query composed of multiple Queryable objects, combined using logical operators."""

    def __init__(
        self,
        queryables: list[Queryable] | None = None,
        logic_operator: LogicOperator = LogicOperator.AND,
    ) -> None:
        """Initializes a Query.

        Args:
            queryables (list[Queryable], optional): list of queryable objects.
                Defaults to [].
            logic_operator (LogicOperator, optional): logic operator to use when combining queryables.
                Defaults to LogicOperator.AND.
        """
        self._queryables: list[Queryable] = queryables or []
        self._logic_operator = logic_operator

    def add(self, queryable: Queryable) -> None:
        """Add a Queryable to to the Query.

        Args:
            queryable (Queryable): Queryable to be added.
        """
        self._queryables.append(queryable)

    def __str__(self) -> str:
        """Return a string representation of the query."""
        return f" {self._logic_operator} ".join(
            str(queryable) for queryable in self._queryables
        )

    def evaluate(self, item: BaseModel) -> bool:
        """Evaluate the query against a BaseModel item.

        Args:
            item (BaseModel): the item to evaluate against.

        Returns:
            bool: True if the query is met, False otherwise.
        """
        if self._logic_operator == LogicOperator.AND:
            return all(queryable.evaluate(item) for queryable in self._queryables)
        elif self._logic_operator == LogicOperator.OR:
            return any(queryable.evaluate(item) for queryable in self._queryables)
        return False


class QueryParser:
    """Parser for converting string queries into Query objects."""

    def parse(self, query: str) -> Query:
        """Parse a string query into a Query object.

        Args:
            query (str): query to parse.

        Returns:
            Query: parsed Query object.
        """
        return Query()


def filter_items(query: Query, items: list[T]) -> list[T]:
    """Filter a list of items based on a query.

    Args:
        query (Query): the query to filter by.
        items (list[T]): the list of items to filter.

    Returns:
        list[T]: A filtered list of items that match the query.
    """
    return [item for item in items if query.evaluate(item)]
