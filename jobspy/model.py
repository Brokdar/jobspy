from datetime import datetime, timedelta

from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    """Data model of a CI/CD Job."""

    id: int | None = Field(default=None, primary_key=True)
    name: str
    status: str
    project: str
    commit_id: str
    runner: str | None = None
    job_url: str
    pipeline_url: str
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration: timedelta | None = None
    queued_duration: timedelta | None = None
    failure_reason: str | None = None
