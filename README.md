# 🎵 MyMusic Downloader (v1.6.3)

A high-performance, silent CLI tool designed to download Spotify playlists directly into your local folder as high-quality MP3s with 100% accurate metadata. No extra folders, no hidden history files—just your music, exactly where you run the command.

## ✨ Features
* **Direct Download**: Songs land in your current directory. No more nested 'downloads' folders.
* **Zero-File History**: It checks your actual folder to see if an MP3 exists before downloading. It never "lies" about progress.
* **Lean UI**: A single, clean progress bar that respects your terminal space.
* **MusicBrainz Integration**: Uses verified metadata to avoid "remix" or "cover" mismatches.
* **Global Access**: Run the 'music' command from any folder (e.g., D:/Music/Workout) and the songs go there.

## 🚀 Installation
1. Ensure you have FFmpeg (https://ffmpeg.org/) installed and in your system PATH.
2. Install/Update globally:
   pip install -U mymusic-dl-Rajthespaceman

## 📖 How to Use
1. Open your terminal in the folder where you want your music.
2. Run 'music' to process your 'playlist.csv' from Exportify.
3. Use 'music -s "Artist - Song"' to grab a quick track.

## 🛠️ CLI Commands
* music: Downloads from 'playlist.csv' in the current folder.
* music --open: Instantly pops open your current music folder.
* music -v: Check your version (Current: 1.4.0).
* music -h: View the direct-folder help menu.

## 📝 Note
This version (1.4.0) has removed the 'backup' folder requirement. The tool now uses your actual music files as the source of truth for resume/skip logic.