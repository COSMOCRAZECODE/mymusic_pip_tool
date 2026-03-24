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
        return "1.4.4" 

__version__ = get_version()

def run_from_csv(csv_file):
    """Main execution logic for processing the CSV file."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    failed_file = os.path.join(backup_dir, "failed_songs.txt") 
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # --- 1. SMART SYNC: Check Current Folder AND 'downloads' Subfolder ---
    downloaded_history = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            stored_names = [line.strip() for line in h.readlines() if line.strip()]
        
        valid_history = []
        for name in stored_names:
            # Check if file exists in current dir OR downloads subfolder
            if os.path.exists(f"{name}.mp3") or os.path.exists(os.path.join("downloads", f"{name}.mp3")):
                valid_history.append(name)
        
        if len(valid_history) != len(stored_names):
            diff = len(stored_names) - len(valid_history)
            print(f"🧹 Syncing: Removed {diff} ghost entries (Files not found in current or downloads folder).")
            with open(history_file, "w", encoding="utf-8") as h:
                for name in valid_history: h.write(f"{name}\n")
            downloaded_history = valid_history
        else:
            downloaded_history = stored_names

    if not os.path.exists(csv_file):
        print(f"🎵 PRO MUSIC PIPELINE v{__version__}")
        print("-" * 40)
        print(f"❌ Error: '{csv_file}' not found!")
        return

    # --- 2. Load Songs ---
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

    # --- 3. Process Songs with Dual-Folder Skip Logic ---
    failed_songs = []
    pbar = tqdm(songs, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    for query in pbar:
        # Check physical existence in BOTH possible locations
        file_physically_exists = os.path.exists(f"{query}.mp3") or os.path.exists(os.path.join("downloads", f"{query}.mp3"))
        
        if query in downloaded_history and file_physically_exists:
            continue

        success = False
        retries = 3 
        
        for attempt in range(retries):
            try:
                if " - " in query:
                    s_name, a_name = query.split(" - ", 1)
                    data = get_clean_metadata(s_name, a_name)
                else:
                    data = None

                path = download_song(query)
                
                # VERIFY BEFORE WRITING (Checks if downloader put it anywhere valid)
                if path and os.path.exists(path):
                    if data:
                        apply_metadata(path, data)
                    
                    with open(history_file, "a", encoding="utf-8") as h:
                        h.write(f"{query}\n")
                    success = True
                    break 
                    
            except Exception:
                continue 
        
        if not success:
            failed_songs.append(query)
            with open(failed_file, "a", encoding="utf-8") as f:
                f.write(f"{query}\n")

    # --- 4. Final Report ---
    print("\n✨ Process Complete!")
    if failed_songs:
        print(f"\n❌ The following {len(failed_songs)} songs failed after {retries} attempts:")
        for f_song in failed_songs:
            print(f"  - {f_song}")
        print(f"\n📝 Check '{failed_file}' for the full list.")
    else:
        print("✅ All songs are synced!")

def main():
    """Entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        prog="music",
        description=f"🎵 PRO MUSIC PIPELINE v{__version__}: Dual-folder aware downloader.",
        epilog="Tracking data is stored in the 'backup' folder."
    )
    
    parser.add_argument("-i", "--input", help="CSV path", default="playlist.csv")
    parser.add_argument("-s", "--search", help="Single search", default=None)
    parser.add_argument("--open", help="Open music folder", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    if args.open:
        # Prefer opening the downloads folder if it exists
        path = os.path.abspath("downloads") if os.path.exists("downloads") else os.getcwd()
        if os.name == 'nt':
            os.startfile(path)
        else:
            subprocess.run(['open' if 'darwin' in os.sys.platform else 'xdg-open', path])
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