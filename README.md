# musefetch

> YouTube Music playlist downloader for Termux on Android.

Paste a YT Music playlist link, get properly tagged audio files in your phone's Music folder. No bloat, no GUI frameworks, no root.

## What It Does

- **Playlist-aware**: Paste any `music.youtube.com/playlist` link
- **Smart metadata**: Artist, title, album, track number — all embedded via mutagen
- **Square artwork**: Auto-crops thumbnails to 1:1 so your music player looks clean
- **Resume support**: Interrupted downloads continue where they left off
- **M4A/AAC output**: Better metadata support than MP3 on mobile players
- **Saves to native Music folder**: Files appear instantly in your default music app

## Requirements

- Android 7+ with [Termux](https://f-droid.org/packages/com.termux/) (install from **F-Droid**, not Play Store)
- ~150MB free storage for dependencies
- Optional: [Termux:API](https://f-droid.org/packages/com.termux.api/) for clipboard integration

## One-Shot Install

Copy and paste this entire block into Termux, then press Enter:

```bash
termux-setup-storage && pkg update -y && pkg install -y python ffmpeg git && pip install --upgrade pip && pip install yt-dlp textual rich mutagen Pillow && git clone https://github.com/nabilfp/musefetch.git ~/musefetch && cd ~/musefetch && pip install -e . && echo '✓ musefetch installed. Type: musefetch'
```

After installation, simply run:

```bash
musefetch
```

## Manual Install (if one-shot fails)

If the command above fails (usually due to RAM limits on low-end devices), run each step separately:

```bash
# 1. Grant storage permission
termux-setup-storage

# 2. Update package lists
pkg update -y

# 3. Install system dependencies (if ffmpeg fails, run: pkg install x264 x265 libvpx opus libogg && pkg install ffmpeg)
pkg install -y python ffmpeg git

# 4. Install Python libraries
pip install --upgrade pip
pip install yt-dlp textual rich mutagen Pillow

# 5. Clone and install musefetch
git clone https://github.com/nabilfp/musefetch.git ~/musefetch
cd ~/musefetch
pip install -e .

# 6. Run
musefetch
```

## Usage

1. Open YouTube Music app → open any playlist → **Share** → **Copy link**
2. Back to Termux, tap the **📋** button (or paste manually)
3. Hit **fetch playlist** — track list loads in ~2 seconds
4. Hit **start download** — watch per-track progress with ETA
5. Find your music in your phone's Music app under `Musefetch/` folder

## Architecture

```
musefetch/
├── core/
│   ├── parser.py      # YT Music playlist extraction (no download)
│   ├── downloader.py  # yt-dlp wrapper with async progress hooks
│   └── postprocess.py # mutagen metadata repair + square thumbnail crop
├── ui/
│   ├── app.tcss       # Dark minimal stylesheet
│   ├── widgets.py     # URLInput, TrackTable, OverallProgress
│   └── screens.py     # MainScreen + ProgressScreen
├── config.py          # Paths, yt-dlp presets, constants
└── app.py             # Textual App entry point
```

## Design Decisions

| Choice | Reason |
|--------|--------|
| **TUI over GUI** | Termux can't run Android native UI without extra plugins. TUI is native, fast, zero overhead. |
| **Textual over npyscreen/urwid** | Modern reactive framework. CSS-like styling. Doesn't look like a 90s DOS app. |
| **M4A over MP3** | Native AAC with better metadata embedding. yt-dlp handles thumbnail embed to M4A flawlessly. |
| **Square thumbnails** | Most mobile music players expect 1:1 artwork. We crop center-square via PIL before embedding. |
| **No sudo anywhere** | Termux is user-space only. All operations respect Android scoped storage. |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `clipboard unavailable` | Install Termux:API from F-Droid, then run `pkg install termux-api` |
| `ffmpeg: cannot locate symbol` | Run `pkg upgrade -y` to fix library linking |
| `SyntaxError` in Python files | Re-clone repo: `rm -rf ~/musefetch && git clone ...` |
| Samsung Music doesn't show files | Run `termux-media-scan ~/storage/music/` or restart phone |
| Download stops midway | Run `musefetch` again with same URL — yt-dlp skips existing files |

## License

MIT — do whatever. If you improve it, send a PR.

## Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the heavy lifting
- [Textual](https://github.com/Textualize/textual) for the beautiful TUI
- [mutagen](https://github.com/quodlibet/mutagen) for metadata surgery
