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
        return "1.3.2" 

__version__ = get_version()

def run_from_csv(csv_file):
    """Main execution logic for processing the CSV file."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    failed_file = os.path.join(backup_dir, "failed_songs.txt") 
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 1. --- REALITY CHECK: Sync History/Failed with Downloads Folder ---
    downloaded_history = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            stored_names = [line.strip() for line in h.readlines() if line.strip()]
        
        # Keep ONLY names that physically have an .mp3 file on disk
        valid_history = [name for name in stored_names if os.path.exists(os.path.join("downloads", f"{name}.mp3"))]
        
        if len(valid_history) != len(stored_names):
            diff = len(stored_names) - len(valid_history)
            print(f"🧹 Syncing History: Removed {diff} ghost entries (Files missing from downloads).")
            with open(history_file, "w", encoding="utf-8") as h:
                for name in valid_history: h.write(f"{name}\n")
            downloaded_history = valid_history
        else:
            downloaded_history = stored_names

    # Clean up the Failed Songs list if they actually exist now
    if os.path.exists(failed_file):
        with open(failed_file, "r", encoding="utf-8") as f:
            failed_names = [line.strip() for line in f.readlines() if line.strip()]
        
        still_failed = [name for name in failed_names if not os.path.exists(os.path.join("downloads", f"{name}.mp3"))]
        with open(failed_file, "w", encoding="utf-8") as f:
            for name in still_failed: f.write(f"{name}\n")

    if not os.path.exists(csv_file):
        print(f"🎵 PRO MUSIC PIPELINE v{__version__}")
        print("-" * 40)
        print(f"❌ Error: '{csv_file}' not found!")
        return

    # 2. --- Load Songs ---
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

    # 3. --- Process Songs ---
    pbar = tqdm(songs, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    for query in pbar:
        # Standard skip check against our verified history
        if query in downloaded_history:
            continue

        try:
            # Metadata fetching
            if " - " in query:
                s_name, a_name = query.split(" - ", 1)
                data = get_clean_metadata(s_name, a_name)
            else:
                data = None

            # Download attempt
            path = download_song(query)
            
            # CRITICAL CHECK: Does the file actually exist at the returned path?
            if path and os.path.exists(path):
                if data:
                    apply_metadata(path, data)
                
                # ONLY write to history if the file is physically verified
                with open(history_file, "a", encoding="utf-8") as h:
                    h.write(f"{query}\n")
            else:
                # If download reported success but file is missing, log to failed
                with open(failed_file, "a", encoding="utf-8") as f:
                    f.write(f"{query}\n")
                
        except Exception:
            with open(failed_file, "a", encoding="utf-8") as f:
                f.write(f"{query}\n")
            continue

    print("\n✨ Process Complete! Your library and history are perfectly in sync.")

def main():
    """Entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        prog="music",
        description=f"🎵 PRO MUSIC PIPELINE v{__version__}: A professional CLI downloader.",
        epilog=f"Thanks for using MyMusic! (Version {__version__})"
    )
    
    parser.add_argument("-i", "--input", help="Path to playlist.csv", default="playlist.csv")
    parser.add_argument("-s", "--search", help="Single song search", default=None)
    parser.add_argument("--open", help="Open downloads folder", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    if args.open:
        path = os.path.abspath("downloads")
        if os.path.exists(path):
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.run(['open' if os.sys.platform == 'darwin' else 'xdg-open', path])
        return

    if args.search:
        path = download_song(args.search)
        if path and os.path.exists(path):
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