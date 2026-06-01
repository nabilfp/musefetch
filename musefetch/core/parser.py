"""Playlist parser."""
import yt_dlp
from dataclasses import dataclass
from typing import List

@dataclass
class Track:
    idx: int
    title: str
    artist: str
    album: str
    duration: int
    video_id: str
    url: str

class PlaylistParser:
    def __init__(self, quiet=True):
        self.opts = {"quiet": quiet, "no_warnings": quiet, "extract_flat": True, "skip_download": True}

    def parse(self, url: str) -> dict:
        with yt_dlp.YoutubeDL(self.opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if info is None:
            raise ValueError("Could not extract playlist info.")
        entries = info.get("entries") or []
        tracks = []
        for i, entry in enumerate(entries, start=1):
            if entry is None:
                continue
            vid = entry.get("id")
            if not vid:
                continue
            tracks.append(Track(
                idx=i,
                title=entry.get("title", "Unknown"),
                artist=entry.get("artist") or entry.get("uploader", "Unknown"),
                album=entry.get("album") or info.get("title", "Unknown Album"),
                duration=entry.get("duration") or 0,
                video_id=vid,
                url=f"https://music.youtube.com/watch?v={vid}",
            ))
        return {
            "title": info.get("title", "Untitled Playlist"),
            "uploader": info.get("uploader", "Unknown"),
            "track_count": len(tracks),
            "tracks": tracks,
        }
