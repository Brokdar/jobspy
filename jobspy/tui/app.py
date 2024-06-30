from pathlib import Path

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.validation import ValidationResult, Validator
from textual.widgets import DataTable, Footer, Header, Input

from jobspy.model import generate_dummy_jobs
from jobspy.tui.job_details import JobDetails
from jobspy.tui.job_master import JobMaster


class FilterValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        if " " in value:
            return self.failure("Must not contain any spaces")
        return self.success()


class JobSpy(App):
    """An application to spy on Gitlab CI jobs."""

    TITLE = "JobSpy"
    SUB_TITLE = "One Spy to watch them all"
    CSS_PATH = "app.tcss"

    BINDINGS = [("ctrl+f", "filter_jobs", "filter jobs")]

    def __init__(self, config: Path | None = None):
        self.config = config
        self.jobs = generate_dummy_jobs()
        self.master = JobMaster(cursor_type="row")
        self.details = JobDetails()
        super().__init__()

    def compose(self) -> ComposeResult:
        """Setup the user interface of the application."""
        yield Header()
        yield Input(placeholder="Apply filter", validators=[FilterValidator()])
        with Horizontal():
            yield self.master
            yield self.details
        yield Footer()

    def on_mount(self):
        self.master.add_column("Name", width=25)
        self.master.add_column("Project", width=16)
        self.master.add_column("Runner", width=16)
        self.master.add_column("Status", width=16)
        self.master.add_column("Finished On", width=20)
        self.master.add_column("Duration", width=10)

        for job in self.jobs:
            self.master.add_row(
                job.name,
                job.project,
                job.runner if job.runner else "",
                Text(job.status, style="italic"),
                job.finished_on.strftime("%Y-%m-%d %H:%M:%S")
                if job.finished_on
                else "",
                Text(str(job.duration) if job.duration else "", justify="right"),
            )

        self.details.update_job(self.jobs[0])
        self.master.focus()

    @on(Input.Submitted)
    def handle_input_submission(self, event: Input.Submitted) -> None:
        if event.validation_result and event.validation_result.is_valid:
            self.apply_filter(event.value)

    def action_filter_jobs(self) -> None:
        input = self.query_one("Input")
        input.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.details.update_job(self.jobs[event.cursor_row])

    def apply_filter(self, filter: str) -> None: ...
