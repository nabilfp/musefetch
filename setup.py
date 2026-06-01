from setuptools import setup, find_packages

setup(
    name="musefetch",
    version="1.0.0",
    description="YouTube Music playlist downloader for Termux",
    author="nabilfp",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2025.12.0",
        "textual>=0.83.0",
        "rich>=13.0.0",
        "mutagen>=1.47.0",
        "Pillow>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "musefetch=musefetch.app:main",
        ],
    },
    python_requires=">=3.10",
)
