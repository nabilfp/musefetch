"""Main and Progress screens."""

import subprocess
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static, Button, Input, Log
from textual.reactive import reactive
from textual.worker import get_current_worker

from musefetch.config import APP_TITLE, APP_VERSION
from musefetch.core.parser import PlaylistParser, Track
from musefetch.core.downloader import Downloader, ProgressEvent
from musefetch.core.postprocess import repair
from musefetch.ui.widgets import URLInput, TrackTable, OverallProgress


class MainScreen(Screen):
    CSS_PATH = "app.tcss"
    _mode = reactive("idle")

    def compose(self) -> ComposeResult:
        with Vertical(id="main-container"):
            yield Static(f"{APP_TITLE} v{APP_VERSION}", id="logo")
            yield Static("paste a YT Music playlist link. we handle the rest.", id="subtitle")
            yield URLInput()
            yield Button("fetch playlist", id="action-btn", variant="primary")
            yield Static("", id="status-msg")
            yield TrackTable(id="track-list")

    def on_mount(self):
        self.query_one("#track-list", TrackTable).display = False

    def watch__mode(self, mode):
        btn = self.query_one("#action-btn", Button)
        btn.label = {"idle":"fetch playlist","fetching":"fetching...","ready":"start download"}.get(mode, "fetch playlist")
        btn.disabled = (mode == "fetching")

    def on_button_pressed(self, ev):
        bid = ev.button.id
        if bid == "paste-btn":
            self._paste()
        elif bid == "action-btn":
            if self._mode == "idle": self._fetch()
            elif self._mode == "ready":
                info = getattr(self, "_info", None)
                if info: self.app.push_screen(ProgressScreen(info))

    def _paste(self):
        inp = self.query_one("#url-input", Input)
        for cmd in (["termux-clipboard-get"],["xclip","-selection","clipboard","-o"],["wl-paste"]):
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=3, check=False)
                if r.returncode == 0 and r.stdout.strip():
                    inp.value = r.stdout.strip()
                    self._status("clipboard pasted ✓"); return
            except: pass
        self._status("clipboard unavailable — paste manually")

    def _status(self, msg):
        self.query_one("#status-msg", Static).update(msg)

    def _fetch(self):
        url = self.query_one("#url-input", Input).value.strip()
        if not url: self._status("paste a link first"); return
        if "music.youtube.com" not in url and "youtube.com/playlist" not in url:
            self._status("only YT Music playlists are supported"); return
        self._mode = "fetching"; self._status("reading playlist...")
        self.run_worker(self._do_fetch(url), thread=True)

    async def _do_fetch(self, url):
        w = get_current_worker()
        try:
            info = PlaylistParser().parse(url)
            if w.is_cancelled: return
            await self._preview(info)
        except Exception as e:
            await self._error(str(e))

    async def _preview(self, info):
        t = self.query_one("#track-list", TrackTable)
        t.clear(); t.display = True
        for tr in info["tracks"]: t.add_row(str(tr.idx), tr.title, tr.artist, "pending")
        self._info = info; self._mode = "ready"
        self._status(f"{info['track_count']} tracks found — ready to download")

    async def _error(self, msg):
        self._mode = "idle"; self._status(f"error: {msg}")


class ProgressScreen(Screen):
    CSS_PATH = "app.tcss"

    def __init__(self, info, **kw):
        super().__init__(**kw)
        self.info = info
        self.tracks = info["tracks"]
        self.dl = Downloader(self._on_event)
        self._cancel = False

    def compose(self) -> ComposeResult:
        with Vertical(id="progress-container"):
            yield Static(f"downloading: {self.info['title']}", id="progress-title")
            yield TrackTable(id="track-list")
            yield OverallProgress(id="overall-progress")
            yield Log(id="log-output", highlight=True)
            with Horizontal(id="btn-row"):
                yield Button("cancel", id="cancel-btn", variant="error")
                yield Button("done", id="done-btn", variant="success", disabled=True)

    def on_mount(self):
        t = self.query_one("#track-list", TrackTable)
        t.clear()
        for tr in self.tracks: t.add_row(str(tr.idx), tr.title, tr.artist, "queued")
        p = self.query_one("#overall-progress", OverallProgress)
        p.total = len(self.tracks)
        self.run_worker(self._run(), thread=True)

    def on_button_pressed(self, ev):
        if ev.button.id == "cancel-btn":
            self._cancel = True; self.dl.cancel()
            self.query_one("#log-output", Log).write_line("cancel requested...")
        elif ev.button.id == "done-btn":
            self.app.pop_screen()

    def _on_event(self, ev):
        self.app.call_from_thread(self._upd, ev)

    def _upd(self, ev):
        t = self.query_one("#track-list", TrackTable)
        log = self.query_one("#log-output", Log)
        p = self.query_one("#overall-progress", OverallProgress)
        idx = ev.track_idx - 1
        if ev.kind == "start":
            if idx < t.row_count: t.update_cell_at((idx,3), "downloading...")
            log.write_line(f"[{ev.track_idx}] start → {ev.filename}")
        elif ev.kind == "progress":
            if idx < t.row_count:
                pct = (ev.downloaded/ev.total*100) if ev.total else 0
                t.update_cell_at((idx,3), f"{pct:.0f}%")
        elif ev.kind == "postprocess":
            if idx < t.row_count: t.update_cell_at((idx,3), "processing...")
            log.write_line(f"[{ev.track_idx}] {ev.message}")
        elif ev.kind == "finish":
            if idx < t.row_count: t.update_cell_at((idx,3), "done ✓")
            p.completed += 1
            log.write_line(f"[{ev.track_idx}] finished ✓")
            self._pp(idx)
        elif ev.kind == "error":
            if idx < t.row_count: t.update_cell_at((idx,3), "failed ✗")
            log.write_line(f"[{ev.track_idx}] error: {ev.error}")
            p.completed += 1
        if p.completed >= p.total:
            self.query_one("#done-btn", Button).disabled = False
            self.query_one("#cancel-btn", Button).disabled = True

    def _pp(self, idx):
        tr = self.tracks[idx]
        safe = "".join(c for c in self.info["title"] if c not in '\\/:*?"<>|')[:60]
        out = Path.home() / "storage/music/Musefetch" / safe
        cands = list(out.glob(f"*{tr.video_id}*"))
        if not cands: cands = list(out.glob(f"{tr.idx:02d}*"))
        if cands:
            fp = cands[0]
            th = fp.with_suffix(".png")
            if not th.exists(): th = fp.with_suffix(".jpg")
            repair(fp, tr.title, tr.artist, tr.album, tr.idx, th if th.exists() else None)

    async def _run(self):
        await self.dl.download_playlist(self.tracks, self.info["title"])
        if not self._cancel:
            self.app.call_from_thread(self._done)

    def _done(self):
        self.query_one("#log-output", Log).write_line("all tracks processed.")
        self.query_one("#done-btn", Button).disabled = False
        self.query_one("#cancel-btn", Button).disabled = True
