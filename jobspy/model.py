import random
import string
from datetime import datetime, timedelta

from pydantic import BaseModel


class Job(BaseModel):
    """Data model of a CI/CD Job."""

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


def generate_dummy_jobs(count: int = 10) -> list[Job]:
    statuses = ["running", "completed", "failed", "queued", "canceled"]
    projects = ["TC3 - MMA", "TC3 - MB.EA-M", "TC3 - MB.EA-L", "U2B - MB.EA-L"]
    runners = ["runner-1", "runner-2", "runner-3", None]

    dummy_jobs = []
    for i in range(count):
        # Generate random data
        name = f"job-{i+1}"
        status = random.choice(statuses)
        project = random.choice(projects)
        commit_id = "".join(random.choices(string.hexdigits, k=40)).lower()
        runner = random.choice(runners)
        job_url = f"https://example.com/jobs/{name}"
        pipeline_url = f"https://example.com/pipelines/{project}/{commit_id[:8]}"

        created_at = datetime.now() - timedelta(hours=random.randint(1, 48))
        started_at = created_at + timedelta(minutes=random.randint(0, 30))

        if status in ["completed", "failed"]:
            finished_at = started_at + timedelta(minutes=random.randint(5, 60))
            duration = finished_at - started_at
            queued_duration = started_at - created_at
        else:
            finished_at = None
            duration = None
            queued_duration = None

        failure_reason = None
        if status == "failed":
            failure_reason = random.choice(["Script failure", "Timeout error"])

        # Create Job instance
        job = Job(
            name=name,
            status=status,
            project=project,
            commit_id=commit_id,
            runner=runner,
            job_url=job_url,
            pipeline_url=pipeline_url,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            duration=duration,
            queued_duration=queued_duration,
            failure_reason=failure_reason,
        )

        dummy_jobs.append(job)

    return dummy_jobs
