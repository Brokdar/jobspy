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
            ["Created At", job.created_at.strftime("%Y-%m-%d %H:%M:%S")],
            [
                "Finished On",
                job.finished_on.strftime("%Y-%m-%d %H:%M:%S")
                if job.finished_on
                else None,
            ],
            ["Duration", str(job.duration) if job.duration else ""],
            ["Link", job.link],
            ["Return Code", str(job.return_code)],
            ["Error", job.error],
        ]
        for row in rows:
            table.add_row(*row)

        self.update(table)
