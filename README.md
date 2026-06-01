# musefetch

> YouTube Music playlist downloader, built specifically for Termux on Android.

No bloat. No GUI frameworks. No root. Paste a YT Music playlist link, get properly tagged audio files in your phone's Music folder.

## Quick Install

```bash
pkg install python ffmpeg git
pip install yt-dlp textual rich mutagen Pillow
git clone https://github.com/nabilfp/musefetch.git ~/musefetch
cd ~/musefetch && pip install -e .
musefetch
```

## Usage

1. Tap the 📋 button (or paste manually) your YT Music playlist URL
2. Hit **fetch playlist** — preview loads instantly
3. Hit **start download** — watch per-track progress
4. Find your music in your phone's Music app under `Musefetch/`

## License

MIT
