"''Post-process: fix tags, square cover art.'""'' 'from pathlib import Path' 'from typing import Optional' 'import tempfile' 'from mutagen.mp4 import MP4, MP4Cover' 'from mutagen.id3 import ID3, APIC' 'from PIL import Image' '' 'def _sq(thumb, size=800):' '    with Image.open(thumb) as img:' '        w,h = img.size' '        s = min(w,h)' '        l,t = (w-s)//2, (h-s)//2' '        c = img.crop((l,t,l+s,t+s)).resize((size,size), Image.LANCZOS)' '        b = tempfile.BytesIO()' '        c.save(b, format=PNG)' '        return b.getvalue()' '' 'def repair(path, title, artist, album, num, thumb=None):' '    ext = path.suffix.lower()' '    if ext == .m4a:' '        try:' '            a = MP4(str(path))' '            a.tags[xA9nam]=title; a.tags[xA9ART]=artist; a.tags[xA9alb]=album; a.tags[trkn]=[(num,0)]' '            if thumb and thumb.exists():' '                a.tags[covr]=[MP4Cover(_sq(thumb), imageformat=MP4Cover.FORMAT_PNG)]' '            a.save()' '        except: pass' '    elif ext == .mp3:' '        try:' '            from mutagen.mp3 import MP3' '            a = MP3(str(path))' '            if a.tags is None: a.add_tags()' '            a.tags[TIT2]=title; a.tags[TPE1]=artist; a.tags[TALB]=album; a.tags[TRCK]=str(num)' '            if thumb and thumb.exists():' '                a.tags[APIC]=APIC(3,image/png,3,Cover,_sq(thumb))' '            a.save()' '        except: pass' > musefetch/core/postprocess.py
touch musefetch/ui/__init__.py
printf '%s\n' '""Custom
widgets."''
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
