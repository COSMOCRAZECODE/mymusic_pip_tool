import os
import csv
import argparse
import importlib.metadata
import subprocess
from tqdm import tqdm
from .downloader import download_song
from .metadata_fetcher import get_clean_metadata
from .tagger import apply_metadata

# --- AUTOMATIC VERSIONING ---
def get_version():
    try:
        return importlib.metadata.version("mymusic-dl-Rajthespaceman")
    except importlib.metadata.PackageNotFoundError:
        # Single source of truth for local dev fallback
        return "1.3.1" 

__version__ = get_version()

def run_from_csv(csv_file):
    """Main execution logic for processing the CSV file."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    failed_file = os.path.join(backup_dir, "failed_songs.txt") 
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Load history to skip already downloaded songs
    downloaded_history = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            downloaded_history = [line.strip() for line in h.readlines()]

    if not os.path.exists(csv_file):
        print(f"🎵 PRO MUSIC PIPELINE v{__version__} (Exportify Edition)")
        print("-" * 40)
        print(f"❌ Error: '{csv_file}' not found!")
        print("-" * 40)
        return

    songs = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                track = row.get('Track Name')
                artist = row.get('Artist Name(s)')
                if track and artist:
                    songs.append(f"{track} - {artist}")
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}")
        return

    if not songs:
        print("❌ Error: No songs found in the CSV.")
        return

    pbar = tqdm(songs, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    for query in pbar:
        # VERIFICATION CHECK: Skip ONLY if in history AND file actually exists on disk
        # We check the 'downloads' folder for a filename matching the query
        potential_path = os.path.join("downloads", f"{query}.mp3")
        
        if query in downloaded_history and os.path.exists(potential_path):
            continue

        try:
            if " - " in query:
                s_name, a_name = query.split(" - ", 1)
                data = get_clean_metadata(s_name, a_name)
            else:
                data = None

            path = download_song(query)
            
            # SUCCESS CHECK: Confirm file is physically present before updating history
            if path and os.path.exists(path):
                if data:
                    apply_metadata(path, data)
                
                with open(history_file, "a", encoding="utf-8") as h:
                    h.write(f"{query}\n")
            else:
                # Log to failed if download didn't produce a file
                with open(failed_file, "a", encoding="utf-8") as f:
                    f.write(f"{query}\n")
                
        except Exception:
            with open(failed_file, "a", encoding="utf-8") as f:
                f.write(f"{query}\n")
            continue

    print("\n✨ Process Complete! Check the 'downloads' folder.")

def main():
    """Entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        prog="music",
        description=f"🎵 PRO MUSIC PIPELINE v{__version__}: A professional CLI downloader.",
        epilog=f"Thanks for using MyMusic! (Version {__version__})"
    )
    
    parser.add_argument(
        "-i", "--input", 
        help="Path to the playlist.csv file (default: playlist.csv)", 
        default="playlist.csv"
    )
    
    parser.add_argument(
        "-s", "--search", 
        help="Search and download a single song by name (e.g. music -s 'Song Name')", 
        default=None
    )

    parser.add_argument(
        "--open", 
        help="Open the downloads folder in File Explorer", 
        action="store_true"
    )
    
    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if args.open:
        path = os.path.abspath("downloads")
        if os.path.exists(path):
            print(f"📂 Opening: {path}")
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.run(['open' if os.sys.platform == 'darwin' else 'xdg-open', path])
        else:
            print("❌ Downloads folder doesn't exist yet!")
        return

    if args.search:
        print(f"🔎 Searching for: {args.search}")
        path = download_song(args.search)
        if path and os.path.exists(path):
            print(f"✅ Downloaded to: {path}")
            if " - " in args.search:
                s, a = args.search.split(" - ", 1)
                data = get_clean_metadata(s, a)
                if data: apply_metadata(path, data)
        return

    run_from_csv(args.input)

if __name__ == "__main__":
    if not os.path.exists('downloads'): 
        os.makedirs('downloads')
    main()