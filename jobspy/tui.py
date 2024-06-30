from pathlib import Path, PurePath

from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.driver import Driver
from textual.widgets import DataTable, Footer, Header, Static

from jobspy.model import Job, generate_dummy_jobs


class JobMaster(DataTable):
    def action_cursor_up(self) -> None:
        super().action_cursor_up()
        super().action_select_cursor()

    def action_cursor_down(self) -> None:
        super().action_cursor_down()
        super().action_select_cursor()


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


class JobSpy(App):
    """An application to spy on Gitlab CI jobs."""

    TITLE = "JobSpy"
    SUB_TITLE = "One Spy to watch them all"
    CSS_PATH = "tui.tcss"

    def __init__(self, config: Path | None = None):
        self.config = config
        self.jobs = generate_dummy_jobs()
        self.table = JobMaster(cursor_type="row", id="jobs")
        self.details = JobDetails(id="details")
        super().__init__()

    def compose(self) -> ComposeResult:
        """Setup the user interface of the application."""
        yield Header()
        yield self.table
        yield self.details
        yield Footer()

    def on_mount(self):
        self.table.add_column("Name")
        self.table.add_column("Status")
        self.table.add_column("Runner")
        self.table.add_column("Finished On")
        self.table.add_column("Duration")

        for job in self.jobs:
            finished_on = (
                job.finished_on.strftime("%Y-%m-%d %H:%M:%S") if job.finished_on else ""
            )
            duration = str(job.duration) if job.duration else ""
            self.table.add_row(
                job.name,
                Text(job.status, style="italic"),
                job.runner if job.runner else "",
                finished_on,
                Text(duration, justify="right"),
            )

        self.details.update_job(self.jobs[0])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.details.update_job(self.jobs[event.cursor_row])
