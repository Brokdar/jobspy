from rich.text import Text
from textual.widgets import DataTable

from jobspy.model import Job


class JobMaster(DataTable):
    def action_cursor_up(self) -> None:
        super().action_cursor_up()
        super().action_select_cursor()

    def action_cursor_down(self) -> None:
        super().action_cursor_down()
        super().action_select_cursor()

    def add(self, job: Job) -> None:
        self.add_row(
            job.name,
            job.project,
            job.runner if job.runner else "",
            Text(job.status, style="italic"),
            job.finished_on.strftime("%Y-%m-%d %H:%M:%S") if job.finished_on else "",
            Text(str(job.duration) if job.duration else "", justify="right"),
        )
