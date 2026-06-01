"''Playlist parser.'""'' 'import yt_dlp' 'from dataclasses import dataclass' 'from typing import List' '' '@dataclass' 'class Track:' '    idx: int' '    title: str' '    artist: str' '    album: str' '    duration: int' '    video_id: str' '    url: str' '' 'class PlaylistParser:' '    def __init__(self, quiet=True):' '        self.opts = {quiet: quiet, no_warnings: quiet, extract_flat: True, skip_download: True}' '' '    def parse(self, url: str) -> dict:' '        with yt_dlp.YoutubeDL(self.opts) as ydl:' '            info = ydl.extract_info(url, download=False)' '        if info is None:' '            raise ValueError(Could
not
extract
playlist
info.)' '        entries = info.get(entries) or []' '        tracks = []' '        for i, entry in enumerate(entries, start=1):' '            if entry is None:' '                continue' '            vid = entry.get(id)' '            if not vid:' '                continue' '            tracks.append(Track(' '                idx=i,' '                title=entry.get(title, Unknown),' '                artist=entry.get(artist) or entry.get(uploader, Unknown),' '                album=entry.get(album) or info.get(title, Unknown
Album),' '                duration=entry.get(duration) or 0,' '                video_id=vid,' '                url=fhttps://music.youtube.com/watch?v={vid},' '            ))' '        return {' '            title: info.get(title, Untitled
Playlist),' '            uploader: info.get(uploader, Unknown),' '            track_count: len(tracks),' '            tracks: tracks,' '        }' > musefetch/core/parser.py
printf '%s\n' '""Download
engine."''
import asyncio
from pathlib import Path
from dataclasses import dataclass
import yt_dlp
from musefetch.config import BASE_YDL_OPTS, DOWNLOAD_DIR, ensure_dirs

@dataclass
class ProgressEvent:
    kind: str
    track_idx: int = 0
    filename: str = ""
    downloaded: int = 0
    total: int = 0
    speed: float = 0.0
    eta: int = 0
    message: str = ""
    error: str = ""

class Downloader:
    def __init__(self, cb):
        self._cb = cb
        self._cancelled = False
        ensure_dirs()

    def cancel(self):
        self._cancelled = True

    def _hook(self, idx, title):
        def inner(d):
            if self._cancelled:
                raise yt_dlp.utils.DownloadError("cancelled")
            s = d.get("status")
            if s == "downloading":
                t = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                self._cb(ProgressEvent("progress", idx, title, d.get("downloaded_bytes",0), t, d.get("speed",0), d.get("eta",0)))
            elif s == "finished":
                self._cb(ProgressEvent("postprocess", idx, title, message="processing..."))
        return inner

    async def download_track(self, track, pl_title, idx):
        self._cb(ProgressEvent("start", idx, track.title))
        opts = {**BASE_YDL_OPTS}
        safe = "".join(c for c in pl_title if c not in '\\/:*?"<>|')[:60]
        out = DOWNLOAD_DIR / safe
        out.mkdir(parents=True, exist_ok=True)
        opts["outtmpl"] = str(out / "%(track_number)s %(title)s.%(ext)s")
        opts["progress_hooks"] = [self._hook(idx, track.title)]
        loop = asyncio.get_running_loop()
        def run():
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(track.url, download=True)
                return ydl.prepare_filename(info) if info else None
        try:
            r = await loop.run_in_executor(None, run)
        except Exception as e:
            self._cb(ProgressEvent("error", idx, track.title, error=str(e)))
            return None
        if r:
            p = Path(r)
            for e in ("m4a","mp3","ogg","opus","webm"):
                c = p.with_suffix(f".{e}")
                if c.exists():
                    p = c
                    break
            self._cb(ProgressEvent("finish", idx, track.title))
            return p
        return None

    async def download_playlist(self, tracks, title):
        for i, t in enumerate(tracks, 1):
            if self._cancelled:
                break
            await self.download_track(t, title, i)
