from textual.widgets import DataTable


class JobMaster(DataTable):
    def action_cursor_up(self) -> None:
        super().action_cursor_up()
        super().action_select_cursor()

    def action_cursor_down(self) -> None:
        super().action_cursor_down()
        super().action_select_cursor()
