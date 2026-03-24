import yt_dlp
import os

class SilentLogger:
    """Redirects all yt-dlp console output to nowhere to keep the terminal clean."""
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass
    def info(self, msg): pass

def download_song(query):
    # Search for "Official Audio" to help avoid fan-made remixes or covers [cite: 8]
    search_query = f"ytsearch1:{query} Official Audio"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        # Ensure this points to your ffmpeg bin folder [cite: 2]
        'ffmpeg_location': r'C:\Program Files (x86)\ffmpeg\bin',
        'logger': SilentLogger(), 
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # download=True is necessary to trigger the conversion process 
        info = ydl.extract_info(search_query, download=True)
        video_info = info['entries'][0] if 'entries' in info else info
        filename = ydl.prepare_filename(video_info)
        
        # Return the final .mp3 path so the tagger knows where to find the file [cite: 2]
        return os.path.splitext(filename)[0] + ".mp3"