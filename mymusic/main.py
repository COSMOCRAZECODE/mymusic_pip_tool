import os
import csv
import argparse
import importlib.metadata
import subprocess
import hashlib
import re
import time
from tqdm import tqdm
from .downloader import download_song
from .metadata_fetcher import get_clean_metadata
from .tagger import apply_metadata

# --- AUTOMATIC VERSIONING ---
def get_version():
    try:
        return importlib.metadata.version("mymusic-dl-Rajthespaceman")
    except importlib.metadata.PackageNotFoundError:
        return "1.5.3" 

__version__ = get_version()

def get_query_hash(query):
    """Unique 8-char ID based on Exportify Row."""
    return hashlib.md5(query.encode('utf-8')).hexdigest()[:8]

def run_from_csv(csv_file):
    """Main execution logic with Lightweight Hash-Tagging and Verbose Sync."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    failed_file = os.path.join(backup_dir, "failed_songs.txt") 
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. --- LOAD HISTORY ---
    registered_hashes = set()
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            registered_hashes = {line.strip() for line in h if line.strip()}

    # 2. --- SCAN FOR PHYSICAL HASHES ---
    # We find who is actually on disk regardless of the primary filename
    search_dirs = [os.getcwd(), "downloads"]
    physical_hashes = set()
    
    for d in search_dirs:
        if not os.path.exists(d): continue
        for filename in os.listdir(d):
            match = re.search(r'\[([a-f0-9]{8})\]\.mp3$', filename)
            if match:
                physical_hashes.add(match.group(1))

    # 3. --- LOAD CSV & CROSS-CHECK ---
    songs_data = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                track = row.get('Track Name')
                artist = row.get('Artist Name(s)')
                if track and artist:
                    q = f"{track} - {artist}"
                    songs_data.append((q, get_query_hash(q)))
    except Exception as e:
        print(f"❌ CSV Error: {e}"); return

    matched_count = 0
    to_process = []
    for query, q_hash in songs_data:
        # Match only if hash is in TXT AND file is on disk
        if q_hash in registered_hashes and q_hash in physical_hashes:
            matched_count += 1
        else:
            to_process.append((query, q_hash))

    print(f"📊 Total Songs in CSV: {len(songs_data)}")
    print(f"✅ {matched_count} songs matched and verified. Skipping...")
    if to_process:
        print(f"🚀 {len(to_process)} songs to process (new or previously failed).")
    print("-" * 40)

    if not to_process:
        print("✨ Everything is already synced!")
        return

    # 4. --- PROCESS ---
    # Load failed songs into a set to prevent duplicates and allow removals
    failed_set = set()
    if os.path.exists(failed_file):
        with open(failed_file, "r", encoding="utf-8") as f:
            failed_set = {line.strip() for line in f if line.strip()}

    pbar = tqdm(to_process, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    try:
        for query, q_hash in pbar:
            # If we are retrying this song, remove it from failed set first
            failed_set.discard(query)
            
            success = False
            for attempt in range(3):
                temp_path = None
                try:
                    s_name, a_name = query.split(" - ", 1) if " - " in query else (query, "")
                    data = get_clean_metadata(s_name, a_name)
                    
                    # Download using downloader logic
                    temp_path = download_song(query)
                    
                    if temp_path and os.path.exists(temp_path):
                        # --- LIGHTWEIGHT RENAME ---
                        # Append [hash] to whatever the downloader saved
                        time.sleep(0.3) # Give OS a moment to release handle
                        base, ext = os.path.splitext(temp_path)
                        final_path = f"{base} [{q_hash}]{ext}"
                        
                        os.rename(temp_path, final_path)
                        
                        if data:
                            apply_metadata(final_path, data)
                        
                        # --- REGISTER ---
                        with open(history_file, "a", encoding="utf-8") as h:
                            h.write(f"{q_hash}\n")
                        
                        success = True
                        break 
                except Exception:
                    if temp_path and os.path.exists(temp_path):
                        try: os.remove(temp_path)
                        except: pass
                    continue 
            
            if not success:
                failed_set.add(query)

    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted. Cleaning up current session...")
    finally:
        # Overwrite failed file with the cleaned/updated set
        with open(failed_file, "w", encoding="utf-8") as f:
            for item in sorted(failed_set):
                f.write(f"{item}\n")

    print("\n✨ Process Complete!")

def main():
    parser = argparse.ArgumentParser(prog="music")
    parser.add_argument("-i", "--input", help="CSV path", default="playlist.csv")
    parser.add_argument("-s", "--search", help="Single search", default=None)
    parser.add_argument("--open", help="Open folder", action="store_true")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    args = parser.parse_args()

    if args.open:
        path = os.getcwd()
        os.startfile(path) if os.name == 'nt' else subprocess.run(['open', path])
        return

    if args.search:
        h = get_query_hash(args.search)
        path = download_song(args.search)
        if path and os.path.exists(path):
            base, ext = os.path.splitext(path)
            final = f"{base} [{h}]{ext}"
            os.rename(path, final)
            if " - " in args.search:
                s, a = args.search.split(" - ", 1)
                data = get_clean_metadata(s, a)
                if data: apply_metadata(final, data)
        return

    run_from_csv(args.input)

if __name__ == "__main__":
    main()