import os
import csv
import argparse
import importlib.metadata  # New import for versioning
from tqdm import tqdm
from .downloader import download_song
from .metadata_fetcher import get_clean_metadata
from .tagger import apply_metadata

# --- AUTOMATIC VERSIONING ---
try:
    # This pulls the version from the installed package metadata
    __version__ = importlib.metadata.version("mymusic-dl-Rajthespaceman")
except importlib.metadata.PackageNotFoundError:
    # Fallback for when you are running the script locally without installation
    __version__ = "1.1.0"

def run_from_csv(csv_file):
    """Main execution logic for processing the CSV file."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 1. Setup Backup Folder and Files
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    failed_file = os.path.join(backup_dir, "failed_songs.txt") 
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    downloaded_history = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            downloaded_history = [line.strip() for line in h.readlines()]

    # 2. Check for playlist.csv
    if not os.path.exists(csv_file):
        print(f"🎵 PRO MUSIC PIPELINE v{__version__} (Exportify Edition)")
        print("-" * 40)
        print(f"❌ Error: '{csv_file}' not found!")
        print("-" * 40)
        return

    # 3. Load Songs from CSV
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

    # 4. Process Songs (Silent Mode)
    pbar = tqdm(songs, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    for query in pbar:
        if query in downloaded_history:
            continue

        try:
            s_name, a_name = query.split(" - ", 1)
            data = get_clean_metadata(s_name, a_name)
            path = download_song(query)
            
            if path and data and os.path.exists(path):
                apply_metadata(path, data)
                with open(history_file, "a", encoding="utf-8") as h:
                    h.write(f"{query}\n")
            else:
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
        description="🎵 PRO MUSIC PIPELINE: A silent tool to download Spotify playlists using Exportify CSVs."
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
    
    # --- UPDATED VERSION ARGUMENT ---
    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if args.search:
        print(f"🔎 Searching for: {args.search}")
        path = download_song(args.search)
        if path:
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