"""Post-process: fix tags, square cover art."""

from pathlib import Path
from typing import Optional
import tempfile
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC
from PIL import Image


def _sq(thumb, size=800):
    with Image.open(thumb) as img:
        w,h = img.size
        s = min(w,h)
        l,t = (w-s)//2, (h-s)//2
        c = img.crop((l,t,l+s,t+s)).resize((size,size), Image.LANCZOS)
        b = tempfile.BytesIO()
        c.save(b, format="PNG")
        return b.getvalue()


def repair(path, title, artist, album, num, thumb=None):
    ext = path.suffix.lower()
    if ext == ".m4a":
        try:
            a = MP4(str(path))
            a.tags["©nam"]=title; a.tags["©ART"]=artist; a.tags["©alb"]=album; a.tags["trkn"]=[(num,0)]
            if thumb and thumb.exists():
                a.tags["covr"]=[MP4Cover(_sq(thumb), imageformat=MP4Cover.FORMAT_PNG)]
            a.save()
        except: pass
    elif ext == ".mp3":
        try:
            from mutagen.mp3 import MP3
            a = MP3(str(path))
            if a.tags is None: a.add_tags()
            a.tags["TIT2"]=title; a.tags["TPE1"]=artist; a.tags["TALB"]=album; a.tags["TRCK"]=str(num)
            if thumb and thumb.exists():
                a.tags["APIC"]=APIC(3,"image/png",3,"Cover",_sq(thumb))
            a.save()
        except: pass
