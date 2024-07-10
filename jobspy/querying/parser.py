import re
from datetime import datetime, timedelta
from typing import Any

from jobspy.querying.query import (
    ComparisonOperator,
    Condition,
    LogicOperator,
    Query,
    Queryable,
)


class QueryParser:
    """Parser for converting string queries into Query objects."""

    def parse(self, query_str: str) -> Query:
        """Parse the given query string and return a Query object.

        This method tokenizes the input string, then recursively builds a Query
        object by parsing conditions and sub-queries.

        Args:
            query_str (str): The query string to parse.

        Returns:
            Query: The parsed Query object.
        """
        tokens = self._tokenize(query_str)
        return self._parse_query(tokens)

    def _tokenize(self, query_str: str) -> list[str]:
        """Tokenize the query string into a list of tokens.

        This method uses regex to split the query string into tokens, preserving
        quoted strings and handling parentheses as separate tokens.

        Args:
            query_string (str): The query string to tokenize.

        Returns:
            list[str]: A list of tokens.
        """
        pattern = r"\s+\b(AND|OR)\b\s+"
        return [
            token.strip() for token in re.split(pattern, query_str, flags=re.IGNORECASE)
        ]

    def _parse_query(self, tokens: list[str]) -> Query:
        or_group: list[Queryable] = []
        conditions: list[Queryable] = []

        for token in tokens:
            if token.upper() == LogicOperator.OR:
                if conditions:
                    or_group.append(
                        Query(conditions) if len(conditions) > 1 else conditions[0]
                    )
                    conditions = []
            elif token.upper() == LogicOperator.AND:
                continue
            else:
                conditions.append(self._parse_condition(token))

        if conditions:
            or_group.append(Query(conditions) if len(conditions) > 1 else conditions[0])

        if len(or_group) > 1:
            return Query(or_group, LogicOperator.OR)
        else:
            if isinstance(or_group[0], Condition):
                return Query(or_group)
            if isinstance(or_group[0], Query):
                return or_group[0]
            raise TypeError(
                f"Unexpected type: {type(or_group[0])} while parsing the query string"
            )

    def _parse_condition(self, condition_str: str) -> Condition:
        """Parse a condition string into a Condition object.

        This method breaks down a condition string into its components
        (field, operator, value) and creates a Condition object.

        Args:
            condition_str (str): The condition string to parse.

        Returns:
            Condition: The parsed Condition object.

        Raises:
            ValueError: If the condition string is invalid.
        """
        match = re.match(r"(\w+)\s*(=|!=|<=|>=|<|>)\s*(.*)", condition_str)
        if not match:
            raise ValueError(f"Invalid condition format: {condition_str}")

        field, operator, value = match.groups()
        operator = ComparisonOperator(operator)
        value = self._parse_value(value.strip("'\""))

        return Condition(field, operator, value)

    def _parse_value(self, value: str) -> Any:
        """
        Parse a value string into the appropriate data type.

        This method attempts to convert the value string into the best
        matching type (str, int, bool, float, datetime, timedelta).

        Args:
            value (str): The value string to parse.

        Returns:
            Any: The parsed value in its appropriate type.
        """
        # Try parsing as bool
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Try parsing as int
        try:
            return int(value)
        except ValueError:
            pass

        # Try parsing as float
        try:
            return float(value)
        except ValueError:
            pass

        # Try parsing as datetime
        for fmt in (
            "%Y-%m-%d",
            "%y-%m-%d",
            "%Y-%m-%d %H:%M",
            "%y-%m-%d %H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%y-%m-%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass

        # Try parsing as timedelta
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                t = datetime.strptime(value, fmt).time()
                return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            except ValueError:
                pass

        return value
