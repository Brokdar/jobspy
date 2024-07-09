import re
from datetime import datetime, timedelta
from typing import Any

from jobspy.querying.query import ComparisonOperator, Condition, Query


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
        return self._parse_query(query_str)

    def _tokenize(self, query_string: str) -> list[str]:
        """Tokenize the query string into a list of tokens.

        This method uses regex to split the query string into tokens, preserving
        quoted strings and handling parentheses as separate tokens.

        Args:
            query_string (str): The query string to tokenize.

        Returns:
            list[str]: A list of tokens.
        """
        return [query_string]
        # pattern = r"(\(|\)|\S+)"
        # return [
        #     token.strip()
        #     for token in re.findall(pattern, query_string)
        #     if token.strip()
        # ]

    def _parse_query(self, query_str: str) -> Query:
        condition = self._parse_condition(query_str)
        return Query([condition])

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
