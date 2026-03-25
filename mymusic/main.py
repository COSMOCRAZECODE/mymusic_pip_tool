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
        return "1.4.8" 

__version__ = get_version()

def run_from_csv(csv_file):
    """Main execution logic with Mirror-Renaming and Cleanup."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    failed_file = os.path.join(backup_dir, "failed_songs.txt") 
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    search_paths = [os.getcwd(), "downloads"]

    # --- 1. LOAD HISTORY (Set for O(1) Lookup) ---
    downloaded_history = set()
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            downloaded_history = {line.strip() for line in h if line.strip()}

    if not os.path.exists(csv_file):
        print(f"🎵 PRO MUSIC PIPELINE v{__version__}\n❌ Error: '{csv_file}' not found!")
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
        print(f"❌ Failed to read CSV: {e}"); return

    # --- 3. Process ---
    failed_songs = []
    pbar = tqdm(songs, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    # We wrap the loop in a try/except to catch Ctrl+C (KeyboardInterrupt)
    try:
        for query in pbar:
            # SKIP LOGIC: Match history name OR renamed file on disk
            file_exists = os.path.exists(f"{query}.mp3") or os.path.exists(os.path.join("downloads", f"{query}.mp3"))
            if query in downloaded_history and file_exists:
                continue

            success = False
            retries = 3 
            for attempt in range(retries):
                temp_path = None
                try:
                    s_name, a_name = query.split(" - ", 1) if " - " in query else (query, "")
                    data = get_clean_metadata(s_name, a_name)
                    
                    # Download song (might have generic yt-dlp name)
                    temp_path = download_song(query)
                    
                    if temp_path and os.path.exists(temp_path):
                        # --- THE SYNC STEP: RENAME TO MATCH EXPORTIFY EXACTLY ---
                        final_filename = f"{query}.mp3"
                        
                        # Handle potential character conflicts and move to final name
                        os.rename(temp_path, final_filename)
                        
                        if data: 
                            apply_metadata(final_filename, data)
                        
                        # --- THE REGISTRATION STEP ---
                        with open(history_file, "a", encoding="utf-8") as h:
                            h.write(f"{query}\n")
                            
                        success = True
                        break 
                except Exception:
                    # CLEANUP: If rename or download failed, delete the partial/temp file
                    if temp_path and os.path.exists(temp_path):
                        os.remove(temp_path)
                    continue 
            
            if not success:
                failed_songs.append(query)
                with open(failed_file, "a", encoding="utf-8") as f:
                    f.write(f"{query}\n")

    except KeyboardInterrupt:
        print("\n\n🛑 Stop detected! Cleaning up active downloads...")
        # Note: 'temp_path' inside the loop handles the actual file deletion
        return

    print("\n✨ Process Complete!")
    if failed_songs:
        print(f"\n❌ {len(failed_songs)} failures. Check backup/failed_songs.txt")
    else:
        print("✅ All songs are synced and mirrored!")

def main():
    parser = argparse.ArgumentParser(prog="music")
    parser.add_argument("-i", "--input", help="CSV path", default="playlist.csv")
    parser.add_argument("-s", "--search", help="Single search", default=None)
    parser.add_argument("--open", help="Open folder", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    if args.open:
        path = os.path.abspath("downloads") if os.path.exists("downloads") else os.getcwd()
        os.startfile(path) if os.name == 'nt' else subprocess.run(['open', path])
        return

    if args.search:
        # Single search also follows the rename logic
        path = download_song(args.search)
        if path and os.path.exists(path):
            final_name = f"{args.search}.mp3"
            os.rename(path, final_name)
            if " - " in args.search:
                s, a = args.search.split(" - ", 1)
                data = get_clean_metadata(s, a)
                if data: apply_metadata(final_name, data)
        return

    run_from_csv(args.input)

if __name__ == "__main__":
    main()