from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Protocol, TypeVar, Union, List
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)

class LogicOperator(Enum):
    """Enum representing logical operators for combining query conditions."""
    AND = auto()
    OR = auto()

class ComparisonOperator(Enum):
    """Enum representing comparison operators for query conditions."""
    EQ = "="
    NE = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="

class QueryComponent(Protocol):
    """Protocol defining the interface for query components."""
    def evaluate(self, item: BaseModel) -> bool:
        """Evaluate the query component against a BaseModel item."""
        ...

class Condition(QueryComponent):
    """Represents a single condition in a query."""

    def __init__(self, field: str, operator: ComparisonOperator, value: Any):
        """
        Initialize a Condition.

        :param field: The field to compare.
        :param operator: The comparison operator.
        :param value: The value to compare against.
        """
        self.field = field
        self.operator = operator
        self.value = value

    def __str__(self) -> str:
        """Return a string representation of the condition."""
        return f'{self.field} {self.operator.value} {self.value}'

    def evaluate(self, item: BaseModel) -> bool:
        """
        Evaluate the condition against a BaseModel item.

        :param item: The item to evaluate against.
        :return: True if the condition is met, False otherwise.
        """
        item_value = getattr(item, self.field, None)
        if item_value is None:
            return False

        value = self.value
        if isinstance(item_value, (datetime, timedelta)):
            if isinstance(value, str):
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    raise ValueError(f"Invalid datetime format: {value}")
            elif not isinstance(value, (datetime, timedelta)):
                raise TypeError(f"Cannot compare datetime with {type(value)}")
        elif isinstance(item_value, (int, float)):
            if isinstance(value, str):
                try:
                    value = type(item_value)(value)
                except ValueError:
                    raise ValueError(f"Cannot convert '{value}' to {type(item_value).__name__}")
            elif not isinstance(value, (int, float)):
                raise TypeError(f"Cannot compare {type(item_value).__name__} with {type(value)}")
        elif isinstance(item_value, str):
            item_value = item_value.lower()
            if isinstance(value, str):
                value = value.lower()

        op_func = {
            ComparisonOperator.EQ: lambda x, y: x == y,
            ComparisonOperator.NE: lambda x, y: x != y,
            ComparisonOperator.LT: lambda x, y: x < y,
            ComparisonOperator.GT: lambda x, y: x > y,
            ComparisonOperator.LE: lambda x, y: x <= y,
            ComparisonOperator.GE: lambda x, y: x >= y,
        }

        return op_func[self.operator](item_value, value)

class Query(QueryComponent):
    """Represents a composite query made up of multiple query components."""

    def __init__(self, components: List[QueryComponent] = None, logic: LogicOperator = LogicOperator.AND):
        """
        Initialize a Query.

        :param components: List of query components.
        :param logic: The logical operator to use when combining components.
        """
        self.logic_operator = logic
        self.components: List[QueryComponent] = components or []

    def add(self, component: QueryComponent):
        """Add a query component to the query."""
        self.components.append(component)

    def __str__(self) -> str:
        """Return a string representation of the query."""
        conditions_str = f' {self.logic_operator.name} '.join(str(condition) for condition in self.components)
        return f"({conditions_str})"

    def evaluate(self, item: BaseModel) -> bool:
        """
        Evaluate the query against a BaseModel item.

        :param item: The item to evaluate against.
        :return: True if the query conditions are met, False otherwise.
        """
        if self.logic_operator == LogicOperator.AND:
            return all(condition.evaluate(item) for condition in self.components)
        elif self.logic_operator == LogicOperator.OR:
            return any(condition.evaluate(item) for condition in self.components)
        return False

class QueryBuilder:
    """Builder class for constructing complex queries."""

    def __init__(self):
        """Initialize a QueryBuilder with an empty query stack."""
        self.query_stack: List[Query] = [Query()]

    def add_condition(self, field: str, operator: str, value: Any) -> 'QueryBuilder':
        """
        Add a condition to the current query.

        :param field: The field to compare.
        :param operator: The comparison operator as a string.
        :param value: The value to compare against.
        :return: The QueryBuilder instance for method chaining.
        """
        condition = Condition(field, ComparisonOperator(operator), value)
        self.query_stack[-1].add(condition)
        return self

    def and_(self) -> 'QueryBuilder':
        """
        Start a new AND group in the query.

        :return: The QueryBuilder instance for method chaining.
        """
        new_query = Query(logic=LogicOperator.AND)
        self.query_stack[-1].add(new_query)
        self.query_stack.append(new_query)
        return self

    def or_(self) -> 'QueryBuilder':
        """
        Start a new OR group in the query.

        :return: The QueryBuilder instance for method chaining.
        """
        new_query = Query(logic=LogicOperator.OR)
        self.query_stack[-1].add(new_query)
        self.query_stack.append(new_query)
        return self

    def end_group(self) -> 'QueryBuilder':
        """
        End the current query group.

        :return: The QueryBuilder instance for method chaining.
        """
        if len(self.query_stack) > 1:
            self.query_stack.pop()
        return self

    def build(self) -> Query:
        """
        Build and return the final query.

        :return: The constructed Query object.
        """
        return self.query_stack[0]

class QueryParser:
    """Parser for converting string queries into Query objects."""

    def parse_query(self, query: str) -> Query:
        """
        Parse a string query into a Query object.

        :param query: The string query to parse.
        :return: The parsed Query object.
        """
        if not query.strip():
            return Query()
        tokens = self._tokenize(query)
        return self._parse_expression(tokens)

    def _tokenize(self, query: str) -> List[str]:
        """
        Tokenize the query string.

        :param query: The query string to tokenize.
        :return: A list of tokens.
        """
        tokens = []
        current_token = ""
        in_quotes = False
        for char in query:
            if char == '"':
                in_quotes = not in_quotes
                current_token += char
            elif char.isspace() and not in_quotes:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
        if current_token:
            tokens.append(current_token)
        return tokens

    def _parse_expression(self, tokens: List[str], min_precedence: int = 0) -> Query:
        """
        Parse an expression from the token list.

        :param tokens: List of tokens to parse.
        :param min_precedence: Minimum precedence level for operators.
        :return: The parsed Query object.
        """
        left = self._parse_condition(tokens)
        
        while tokens and self._get_precedence(tokens[0]) >= min_precedence:
            operator = tokens.pop(0)
            right = self._parse_expression(tokens, self._get_precedence(operator) + 1)
            
            new_query = Query([left, right], LogicOperator[operator.upper()])
            left = new_query
        
        return left

    def _parse_condition(self, tokens: List[str]) -> Union[Condition, Query]:
        """
        Parse a condition from the token list.

        :param tokens: List of tokens to parse.
        :return: The parsed Condition or Query object.
        """
        if tokens[0] == '(':
            tokens.pop(0)  # Remove opening parenthesis
            condition = self._parse_expression(tokens)
            if not tokens or tokens.pop(0) != ')':
                raise ValueError("Mismatched parentheses in query")
            return condition
        else:
            if len(tokens) < 3:
                raise ValueError("Invalid condition format")
            field = tokens.pop(0).lower()
            operator = ComparisonOperator(tokens.pop(0))
            value = tokens.pop(0).strip('"')
            return Condition(field, operator, value)

    def _get_precedence(self, operator: str) -> int:
        """
        Get the precedence of a logical operator.

        :param operator: The operator to check.
        :return: The precedence level of the operator.
        """
        return 2 if operator.upper() == "AND" else 1

def filter_items(query: Query, items: List[T]) -> List[T]:
    """
    Filter a list of items based on a query.

    :param query: The query to filter by.
    :param items: The list of items to filter.
    :return: A filtered list of items that match the query.
    """
    return [item for item in items if query.evaluate(item)]