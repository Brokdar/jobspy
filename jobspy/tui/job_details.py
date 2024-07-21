from rich.color import Color
from rich.style import Style
from rich.table import Table
from textual.widgets import Static

from jobspy.model import Job


class JobDetails(Static):
    """Detail view of a Job."""

    def update_job(self, job: Job) -> None:
        table = Table(
            show_header=False,
            box=None,
            title="Job Details",
            title_style=Style(bgcolor=Color.from_rgb(0x48, 0x3D, 0x8B), bold=True),
            title_justify="center",
        )
        rows: list[list[str | None]] = [
            ["Name", job.name],
            ["Project", job.project],
            ["Runner", job.runner],
            ["Status", job.status],
            ["Commit ID", job.commit_id],
            ["Created At", job.created_at.strftime("%Y-%m-%d %H:%M:%S")],
            [
                "Started At",
                job.started_at.strftime("%Y-%m-%d %H:%M:%S")
                if job.started_at
                else None,
            ],
            [
                "Finished At",
                job.finished_at.strftime("%Y-%m-%d %H:%M:%S")
                if job.finished_at
                else None,
            ],
            ["Duration", str(job.duration) if job.duration else None],
            [
                "Queued Duration",
                str(job.queued_duration) if job.queued_duration else None,
            ],
            ["Pipeline URL", job.pipeline_url],
            ["Job URL", job.job_url],
            ["Failure Reason", job.failure_reason],
        ]
        for row in rows:
            table.add_row(*row)

        self.update(table)
