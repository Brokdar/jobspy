from datetime import datetime, timedelta

from pydantic import BaseModel


class TestItem(BaseModel):
    """Test item for testing the querying."""

    id: int
    name: str
    active: bool
    factor: float
    created_at: datetime
    duration: timedelta
