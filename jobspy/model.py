import random
from datetime import datetime, timedelta

from pydantic import BaseModel


class Job(BaseModel):
    """Data model of a CI/CD Job."""

    name: str
    status: str
    created_on: datetime
    link: str
    project: str
    finished_on: datetime | None = None
    duration: timedelta | None = None
    runner: str | None = None


def generate_dummy_jobs(num_jobs: int = 10) -> list[Job]:
    statuses = ["running", "completed", "failed", "queued", "canceled"]
    projects = ["TC3 - MMA", "TC3 - MB.EA-M", "TC3 - MB.EA-L", "U2B - MB.EA-L"]
    runners = ["runner-1", "runner-2", "runner-3", None]

    dummy_jobs = []
    for i in range(num_jobs):
        created_on = datetime.now() - timedelta(days=random.randint(0, 30))
        status = random.choice(statuses)

        if status in ["completed", "failed"]:
            finished_on = created_on + timedelta(minutes=random.randint(5, 120))
            duration = finished_on - created_on
        else:
            finished_on = None
            duration = None

        job = Job(
            name=f"job-{i+1}",
            status=status,
            created_on=created_on,
            link=f"https://ci-cd.example.com/jobs/job-{i+1}",
            project=random.choice(projects),
            finished_on=finished_on,
            duration=duration,
            runner=random.choice(runners),
        )
        dummy_jobs.append(job)

    return dummy_jobs
