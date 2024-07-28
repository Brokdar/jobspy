import random
import string
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from jobspy.model import Job
from jobspy.querying import filter_items
from jobspy.querying.query import Query


class GitlabClient:
    def __init__(self) -> None:
        """Initializes the Gitlab client."""
        self.__cache: dict[int, Job] = {}
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///db.sqlite", echo=True, future=True
        )
        # self.save()

    async def init(self) -> None:
        async with self.engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

    async def query_jobs(self, query: Query | None = None) -> list[Job]:
        if not self.__cache:
            await self.__load_from_database()

        jobs = (
            self.__cache.values()
            if query is None
            else filter_items(query, self.__cache.values())
        )
        return sorted(jobs, key=lambda job: job.created_at)

    async def refresh(self) -> None:
        jobs: list[Job] = []  # from API request
        updated_jobs = [job for job in jobs if job != self.__cache[job.id]]

        async with AsyncSession(self.engine) as session:
            for job in updated_jobs:
                self.__cache[job.id] = job
                session.add(job)

            await session.commit()

    async def save(self) -> None:
        async with AsyncSession(self.engine) as session:
            statuses = ["running", "completed", "failed", "queued", "canceled"]
            projects = ["TC3 - MMA", "TC3 - MB.EA-M", "TC3 - MB.EA-L", "U2B - MB.EA-L"]
            runners = ["runner-1", "runner-2", "runner-3", None]

            for i in range(100):
                # Generate random data
                name = f"job-{i+1}"
                status = random.choice(statuses)
                project = random.choice(projects)
                commit_id = "".join(random.choices(string.hexdigits, k=40)).lower()
                runner = random.choice(runners)
                job_url = f"https://example.com/jobs/{name}"
                pipeline_url = (
                    f"https://example.com/pipelines/{project}/{commit_id[:8]}"
                )

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

                session.add(job)

            await session.commit()

    async def __load_from_database(self) -> None:
        """Loads all jobs from the database."""
        async with AsyncSession(self.engine) as session:
            for job in await session.exec(select(Job)):
                if job.id is not None:
                    self.__cache[job.id] = job
