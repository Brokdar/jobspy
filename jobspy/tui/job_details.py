from rich.table import Table
from textual.widgets import Static

from jobspy.model import Job


class JobDetails(Static):
    """Detail view of a Job."""

    def update_job(self, job: Job) -> None:
        table = Table(show_header=False, box=None, title="Job Details")
        table.add_row(
            "[label]Name",
            job.name,
            "[label]Status",
            job.status,
            "[label]Runner",
            job.runner if job.runner else "",
        )
        table.add_row(
            "[label]Created On",
            job.created_on.strftime("%Y-%m-%d %H:%M:%S"),
            "[label]Finished On",
            job.finished_on.strftime("%Y-%m-%d %H:%M:%S") if job.finished_on else "",
            "[label]Duration",
            str(job.duration) if job.duration else "",
        )
        table.add_row(
            "[label]Project",
            job.project,
            "[label]Link",
            job.link,
        )

        self.update(table)
