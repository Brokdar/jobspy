import pytest
from pydantic import BaseModel
from datetime import datetime

from jobspy.query_lang import Query, QueryBuilder, QueryParser, filter_items

class TestItem(BaseModel):
    id: int
    name: str
    age: int
    salary: float
    created_at: datetime

@pytest.fixture
def sample_data() -> list[TestItem]:
    return [
        TestItem(id=1, name="Alice", age=30, salary=50000.0, created_at=datetime(2023, 1, 1)),
        TestItem(id=2, name="Bob", age=25, salary=60000.0, created_at=datetime(2023, 2, 1)),
        TestItem(id=3, name="Charlie", age=35, salary=70000.0, created_at=datetime(2023, 3, 1)),
        TestItem(id=4, name="David", age=40, salary=80000.0, created_at=datetime(2023, 4, 1)),
    ]

@pytest.mark.parametrize("query_str, expected_ids", [
    ("age > 30", [3, 4]),
    ("salary <= 60000.0", [1, 2]),
    ('name = "Alice"', [1]),
    ("age >= 35 AND salary < 75000.0", [3]),
    ("age < 30 OR salary > 75000.0", [2, 4]),
    ('(age > 30 AND salary < 75000.0) OR name = "Bob"', [2, 3]),
    ("created_at > 2023-02-15", [3, 4]),
])
def test_query_filtering(sample_data, query_str, expected_ids):
    parser = QueryParser()
    query = parser.parse_query(query_str)
    result = filter_items(query, sample_data)
    assert [item.id for item in result] == expected_ids

def test_empty_query():
    parser = QueryParser()
    query = parser.parse_query("")
    assert isinstance(query, Query)
    assert len(query.components) == 0

def test_invalid_operator():
    parser = QueryParser()
    with pytest.raises(ValueError):
        parser.parse_query("age % 30")

def test_invalid_field(sample_data: list[TestItem]):
    parser = QueryParser()
    query = parser.parse_query("invalid_field = 30")
    result = filter_items(query, sample_data)
    assert len(result) == 0

def test_date_comparison(sample_data: list[TestItem]):
    parser = QueryParser()
    query = parser.parse_query("created_at > 2023-02-15")
    result = filter_items(query, sample_data)
    assert len(result) == 2
    assert all(item.created_at > datetime(2023, 2, 15) for item in result)

def test_complex_query(sample_data: list[TestItem]):
    parser = QueryParser()
    query_str = '(age > 30 AND salary < 75000.0) OR (name = "Bob" AND created_at < 2023-03-01)'
    query = parser.parse_query(query_str)
    result = filter_items(query, sample_data)
    assert len(result) == 2
    assert set([item.id for item in result]) == {2, 3}

def test_query_builder(sample_data: list[TestItem]):
    builder = QueryBuilder()
    query = (builder
        .add_condition("age", ">", "30")
        .and_()
        .add_condition("salary", "<", "75000.0")
        .end_group()
        .or_()
        .add_condition("name", "=", "Bob")
        .build())
    
    result = filter_items(query, sample_data)
    assert len(result) == 2
    assert set([item.id for item in result]) == {2, 3}

def test_query_builder_complex(sample_data: list[TestItem]):
    builder = QueryBuilder()
    query = (builder
        .add_condition("age", ">", "30")
        .and_()
        .add_condition("salary", "<", "75000.0")
        .end_group()
        .or_()
        .and_()
        .add_condition("name", "=", "Bob")
        .add_condition("created_at", "<", "2023-03-01")
        .end_group()
        .build())
    
    result = filter_items(query, sample_data)
    assert len(result) == 2
    assert set([item.id for item in result]) == {2, 3}

def test_invalid_date_format():
    parser = QueryParser()
    with pytest.raises(ValueError):
        parser.parse_query("created_at > invalid_date")

def test_mismatched_parentheses():
    parser = QueryParser()
    with pytest.raises(ValueError):
        parser.parse_query("(age > 30 AND salary < 75000.0")

def test_invalid_condition_format():
    parser = QueryParser()
    with pytest.raises(ValueError):
        parser.parse_query("age > ")

def test_type_mismatch(sample_data: list[TestItem]):
    parser = QueryParser()
    query = parser.parse_query("age > not_a_number")
    with pytest.raises(ValueError):
        filter_items(query, sample_data)
