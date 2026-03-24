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
        return "1.4.0" 

__version__ = get_version()

def run_from_csv(csv_file):
    """Main execution logic for processing the CSV file."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    if not os.path.exists(csv_file):
        print(f"🎵 PRO MUSIC PIPELINE v{__version__}")
        print("-" * 40)
        print(f"❌ Error: '{csv_file}' not found!")
        return

    # 1. --- Load Songs from CSV ---
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

    # 2. --- Process Songs (Checking Current Directory) ---
    failed_songs = []
    current_dir = os.getcwd()
    
    pbar = tqdm(songs, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    for query in pbar:
        # SKIP LOGIC: Check if the file already exists in the current folder
        # We assume the downloader saves as 'Track - Artist.mp3'
        target_file = f"{query}.mp3"
        if os.path.exists(os.path.join(current_dir, target_file)):
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
            
            # Final verification
            if path and os.path.exists(path):
                if data:
                    apply_metadata(path, data)
            else:
                failed_songs.append(query)
                
        except Exception:
            failed_songs.append(query)
            continue

    # 3. --- Final Report ---
    print("\n✨ Process Complete!")
    if failed_songs:
        print(f"\n❌ The following {len(failed_songs)} songs failed:")
        for f_song in failed_songs:
            print(f"  - {f_song}")
        
        # Optional file creation for large failure lists
        if len(failed_songs) > 3:
            choice = input("\nSave these to 'failed_songs.txt'? (y/n): ").lower()
            if choice == 'y':
                with open("failed_songs.txt", "w", encoding="utf-8") as f:
                    for f_song in failed_songs:
                        f.write(f"{f_song}\n")
                print("📝 Saved to failed_songs.txt")
    else:
        print("✅ All songs are synced and downloaded!")

def main():
    """Entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        prog="music",
        description=f"🎵 PRO MUSIC PIPELINE v{__version__}: Direct-to-folder downloader.",
        epilog="Run this inside the folder where you want your music!"
    )
    
    parser.add_argument("-i", "--input", help="CSV path", default="playlist.csv")
    parser.add_argument("-s", "--search", help="Single song search", default=None)
    parser.add_argument("--open", help="Open current folder", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    # Opens the folder where the user currently is
    if args.open:
        path = os.getcwd()
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
    main()