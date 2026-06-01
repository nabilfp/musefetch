"""Custom widgets."""

from textual.widgets import Static, Input, Button, DataTable, ProgressBar
from textual.reactive import reactive
from textual.containers import Horizontal, Vertical


class URLInput(Horizontal):
    def compose(self):
        yield Input(placeholder="paste YT Music playlist link...", id="url-input")
        yield Button("📋", id="paste-btn", variant="primary")


class TrackTable(DataTable):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_columns("#", "Title", "Artist", "Status")
        self.cursor_type = "row"
    def update_track(self, idx, status):
        if idx < self.row_count:
            self.update_cell_at((idx,3), status)


class OverallProgress(Vertical):
    total = reactive(0)
    completed = reactive(0)
    def __init__(self, **kw):
        super().__init__(**kw)
        self._bar = ProgressBar(total=100, show_eta=False)
        self._label = Static("0 / 0 tracks", id="progress-label")
    def compose(self):
        yield self._bar
        yield self._label
    def watch_total(self, t):
        self._bar.update(total=t)
        self._rl()
    def watch_completed(self, c):
        self._bar.update(progress=c)
        self._rl()
    def _rl(self):
        self._label.update(f"{self.completed} / {self.total} tracks • {self._bar.progress}%")
