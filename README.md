# musefetch

> Downloader playlist YouTube Music untuk Termux di Android.

Tempel link playlist YouTube Music, dapatkan file audio dengan metadata lengkap di folder Musik HP-mu. Tanpa bloat, tanpa GUI framework, tanpa root.

## Fitur

- **Mendukung playlist**: Paste link `music.youtube.com/playlist`
- **Metadata otomatis**: Artis, judul, album, nomor track — semua tertanam via mutagen
- **Cover art persegi**: Thumbnail auto-crop 1:1 biar music player HP-mu terlihat rapi
- **Resume download**: Download yang terputus akan dilanjutkan dari file terakhir
- **Output M4A/AAC**: Support metadata lebih baik daripada MP3 di music player mobile
- **Tersimpan di folder Musik**: File langsung muncul di music player bawaan HP

## Persyaratan

- Android 7+ dengan [Termux](https://f-droid.org/packages/com.termux/) (install dari **F-Droid**, bukan Play Store)
- ~150MB storage kosong untuk dependency
- Opsional: [Termux:API](https://f-droid.org/packages/com.termux.api/) untuk integrasi clipboard

## Instalasi Sekali Tempel

Copy dan paste seluruh block ini ke Termux, lalu tekan Enter:

```bash
termux-setup-storage && pkg update -y && pkg install -y python ffmpeg git && pip install --upgrade pip && pip install yt-dlp textual rich mutagen Pillow && git clone https://github.com/nabilfp/musefetch.git ~/musefetch && cd ~/musefetch && pip install -e . && echo '✓ musefetch terinstall. Ketik: musefetch'
```

Setelah instalasi, jalankan:

```bash
musefetch
```

## Instalasi Manual (kalau sekali tempel gagal)

Kalau command di atas gagal (biasanya karena RAM kecil di HP entry-level), jalankan tiap step terpisah:

```bash
# 1. Beri izin storage
termux-setup-storage

# 2. Update daftar package
pkg update -y

# 3. Install dependency sistem (kalau ffmpeg gagal, jalankan: pkg install x264 x265 libvpx opus libogg && pkg install ffmpeg)
pkg install -y python ffmpeg git

# 4. Install library Python
pip install --upgrade pip
pip install yt-dlp textual rich mutagen Pillow

# 5. Clone dan install musefetch
git clone https://github.com/nabilfp/musefetch.git ~/musefetch
cd ~/musefetch
pip install -e .

# 6. Jalankan
musefetch
```

## Cara Pakai

1. Buka aplikasi YouTube Music → buka playlist apapun → **Share** → **Copy link**
2. Kembali ke Termux, tap tombol **📋** (atau paste manual)
3. Tap **fetch playlist** — daftar lagu muncul dalam ~2 detik
4. Tap **start download** — lihat progress per lagu dengan ETA
5. Cek music player HP-mu, folder `Musefetch/` sudah muncul

## Arsitektur

```
musefetch/
├── core/
│   ├── parser.py      # Ekstraksi playlist YT Music (tanpa download)
│   ├── downloader.py  # Wrapper yt-dlp dengan progress hook async
│   └── postprocess.py # Perbaikan metadata mutagen + crop thumbnail persegi
├── ui/
│   ├── app.tcss       # Stylesheet dark minimal
│   ├── widgets.py     # URLInput, TrackTable, OverallProgress
│   └── screens.py     # MainScreen + ProgressScreen
├── config.py          # Path, preset yt-dlp, konstanta
└── app.py             # Entry point Textual App
```

## Keputusan Desain

| Pilihan | Alasan |
|---------|--------|
| **TUI bukan GUI** | Termux tidak bisa menjalankan UI Android native tanpa plugin tambahan. TUI native, cepat, zero overhead. |
| **Textual bukan npyscreen/urwid** | Framework reactive modern. Styling seperti CSS. Tidak terlihat seperti aplikasi DOS era 90an. |
| **M4A bukan MP3** | AAC dengan support metadata embedding lebih baik. yt-dlp handle thumbnail embed ke M4A tanpa masalah. |
| **Thumbnail persegi** | Kebanyakan music player mobile mengharapkan artwork 1:1. Kita crop center-square via PIL sebelum embed. |
| **Tanpa sudo** | Termux hanya user-space. Semua operasi menghormati Android scoped storage. |

## Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `clipboard unavailable` | Install Termux:API dari F-Droid, lalu jalankan `pkg install termux-api` |
| `ffmpeg: cannot locate symbol` | Jalankan `pkg upgrade -y` untuk fix library linking |
| `SyntaxError` di file Python | Re-clone repo: `rm -rf ~/musefetch && git clone ...` |
| Samsung Music tidak muncul file | Jalankan `termux-media-scan ~/storage/music/` atau restart HP |
| Download berhenti di tengah | Jalankan `musefetch` lagi dengan URL sama — yt-dlp skip file yang sudah ada |

## Lisensi

MIT — pakai sesukamu. Kalau ada improvement, kirim PR.

## Kredit

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) untuk heavy lifting
- [Textual](https://github.com/Textualize/textual) untuk TUI yang indah
- [mutagen](https://github.com/quodlibet/mutagen) untuk surgery metadata
