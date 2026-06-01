"""Configuration - paths, constants, yt-dlp presets."""

from pathlib import Path

HOME = Path.home()
STORAGE_MUSIC = HOME / "storage/music"
DOWNLOAD_DIR = STORAGE_MUSIC / "Musefetch"
CACHE_DIR = HOME / ".cache/musefetch"
TEMP_DIR = CACHE_DIR / "tmp"
ARCHIVE_FILE = CACHE_DIR / "archive.txt"


def ensure_dirs():
    for d in (DOWNLOAD_DIR, CACHE_DIR, TEMP_DIR):
        d.mkdir(parents=True, exist_ok=True)


AUDIO_FORMAT = "m4a"
AUDIO_QUALITY = "0"

BASE_YDL_OPTS = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "audioformat": AUDIO_FORMAT,
    "audioquality": AUDIO_QUALITY,
    "outtmpl": str(TEMP_DIR / "%(id)s.%(ext)s"),
    "writethumbnail": True,
    "embedthumbnail": True,
    "addmetadata": True,
    "embedmetadata": True,
    "ignoreerrors": True,
    "noplaylist": False,
    "download_archive": str(ARCHIVE_FILE),
    "concurrent_fragments": 4,
    "quiet": True,
    "no_warnings": True,
    "noprogress": True,
    "progress_hooks": [],
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": AUDIO_FORMAT,
            "preferredquality": AUDIO_QUALITY,
        },
        {
            "key": "EmbedThumbnail",
            "already_have_thumbnail": False,
        },
        {
            "key": "FFmpegMetadata",
            "add_metadata": True,
        },
    ],
    "postprocessor_args": {
        "thumbnailsconvertor+ffmpeg_o": [
            "-c:v", "png",
            "-vf", "crop='if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'",
        ]
    },
    "convertthumbnails": "png",
    "windowsfilenames": True,
    "trimfilenames": 120,
}

APP_TITLE = "musefetch"
APP_VERSION = "1.0.0"
