from collections.abc import Iterable
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.validation import ValidationResult, Validator
from textual.widgets import DataTable, Footer, Input

from jobspy.model import Job, generate_dummy_jobs
from jobspy.querying import filter_items
from jobspy.querying.parser import QueryParser
from jobspy.tui.job_details import JobDetails
from jobspy.tui.job_master import JobMaster


class FilterValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        try:
            QueryParser().parse(value)
        except Exception as error:
            return self.failure(str(error))
        return self.success()


class JobSpy(App):
    """An application to spy on Gitlab CI jobs."""

    TITLE = "JobSpy"
    SUB_TITLE = "One Spy to watch them all"
    CSS_PATH = "app.tcss"

    BINDINGS = [
        ("ctrl+f", "filter_jobs", "filter jobs"),
        ("ctrl+r", "reset_filter", "reset filter"),
    ]

    def __init__(self, config: Path | None = None):
        self.config = config
        self.jobs = generate_dummy_jobs()
        self.master = JobMaster(cursor_type="row")
        self.details = JobDetails()
        self.input = Input(
            placeholder="Apply filter", validators=[FilterValidator()], valid_empty=True
        )
        super().__init__()

    def compose(self) -> ComposeResult:
        """Setup the user interface of the application."""
        yield self.input
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
        self.display_jobs(self.jobs)

    @on(Input.Submitted)
    def handle_input_submission(self, event: Input.Submitted) -> None:
        if event.validation_result and event.validation_result.is_valid:
            self.apply_filter(event.value)

    def action_filter_jobs(self) -> None:
        input = self.query_one("Input")
        input.focus()

    def action_reset_filter(self) -> None:
        self.input.value = ""
        self.display_jobs(self.jobs)
        self.input.focus()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.details.update_job(self.jobs[event.cursor_row])

    def apply_filter(self, filter: str) -> None:
        if filter:
            query = QueryParser().parse(filter)
            jobs = filter_items(query, self.jobs)
            self.display_jobs(jobs)
        else:
            self.display_jobs(self.jobs)

    def display_jobs(self, jobs: Iterable[Job]) -> None:
        self.master.clear()
        first: Job | None = None
        for job in jobs:
            if first is None:
                first = job
            self.master.add(job)

        if first is not None:
            self.details.update_job(first)
        self.master.focus()
