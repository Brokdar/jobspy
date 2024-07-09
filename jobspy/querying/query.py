"""Implements a flexible querying language for filtering lists of data based on various conditions and operators."""

from dataclasses import dataclass, field
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


class QueryError(Exception):
    """Base class for query-related errors."""


class InvalidOperatorError(QueryError):
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


class TypeMismatchError(QueryError):
    """Raised when field value type doesn't match the provided value type."""

    def __init__(self, field_name: str, expected_type: type, actual_type: type) -> None:
        super().__init__(
            f"Type mismatch for field '{field_name}': expected {expected_type}, got {actual_type}"
        )


class Queryable(Protocol):
    """Protocol defining the interface for objects that can be evaluated against a BaseModel item."""

    def evaluate(self, item: T) -> bool:
        """Evaluates the queryable against a T item."""


@dataclass
class Condition(Queryable):
    """Represents a single condition in a query."""

    field: str
    operator: ComparisonOperator
    value: Any

    def __str__(self) -> str:
        """Returns a string representation of the condition."""
        return f"{self.field} {self.operator} {self.value}"

    def evaluate(self, item: T) -> bool:
        """Evaluate the condition against a BaseModel item.

        Args:
            item (T): the item to evaluate against.

        Returns:
            bool: True if the query is met, False otherwise.
        """
        item_value = getattr(item, self.field, None)
        if item_value is None:
            return False

        item_type = type(item_value)
        if not isinstance(self.value, item_type):
            raise TypeMismatchError(self.field, type(item_value), type(self.value))

        if self.operator not in VALID_OPERATOR_MAP[item_type]:
            raise InvalidOperatorError(self.field, item_type, self.operator)

        return OPERATOR_FUNCTION_MAP[self.operator](item_value, self.value)


@dataclass
class Query(Queryable):
    """Represents a complex query composed of multiple Queryable objects, combined using logical operators."""

    queryables: list[Queryable] = field(default_factory=list)
    logic_operator: LogicOperator = LogicOperator.AND

    def __str__(self) -> str:
        """Return a string representation of the query."""
        return f" {self.logic_operator} ".join(
            str(queryable) for queryable in self.queryables
        )

    def add(self, queryable: Queryable) -> None:
        """Add a Queryable to to the Query.

        Args:
            queryable (Queryable): Queryable to be added.
        """
        self.queryables.append(queryable)

    def evaluate(self, item: T) -> bool:
        """Evaluate the query against a BaseModel item.

        Args:
            item (T): the item to evaluate against.

        Returns:
            bool: True if the query is met, False otherwise.
        """
        if self.logic_operator == LogicOperator.AND:
            return all(queryable.evaluate(item) for queryable in self.queryables)
        elif self.logic_operator == LogicOperator.OR:
            return any(queryable.evaluate(item) for queryable in self.queryables)
        return False
