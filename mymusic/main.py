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
        return "1.5.5" 

__version__ = get_version()

def get_query_hash(query):
    return hashlib.md5(query.encode('utf-8')).hexdigest()[:8]

def print_exportify_instructions():
    """Prints a helpful guide if the user is missing their CSV file."""
    print(f"🎵 PRO MUSIC PIPELINE v{__version__}")
    print("-" * 45)
    print("❌ Error: 'playlist.csv' not found!")
    print("\n📝 HOW TO GET YOUR PLAYLIST:")
    print("1. Go to: https://watsonbox.github.io/exportify/")
    print("2. Log in with Spotify and export your desired playlist.")
    print("3. Rename the downloaded file to 'playlist.csv'.")
    print("4. Place it in this folder and run 'music' again.")
    print("-" * 45)

def run_from_csv(csv_file):
    """Main execution logic with Exportify Help and Stable Sync."""
    if not os.path.exists(csv_file):
        print_exportify_instructions()
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    failed_file = os.path.join(backup_dir, "failed_songs.txt") 
    os.makedirs(backup_dir, exist_ok=True)
    
    # 1. LOAD HISTORY
    registered_hashes = set()
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            registered_hashes = {line.strip() for line in h if line.strip()}

    # 2. SCAN PHYSICAL HASHES
    search_dirs = [os.getcwd(), "downloads"]
    physical_hashes = set()
    for d in search_dirs:
        if not os.path.exists(d): continue
        for filename in os.listdir(d):
            match = re.search(r'\[([a-f0-9]{8})\]\.mp3$', filename)
            if match: physical_hashes.add(match.group(1))

    # 3. LOAD CSV
    songs_data = []
    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                t, a = row.get('Track Name'), row.get('Artist Name(s)')
                if t and a:
                    q = f"{t} - {a}"
                    songs_data.append((q, get_query_hash(q)))
    except Exception as e:
        print(f"❌ Failed to read CSV: {e}"); return

    # Match check
    to_process = []
    matched_count = 0
    for query, q_hash in songs_data:
        if q_hash in registered_hashes and q_hash in physical_hashes:
            matched_count += 1
        else:
            to_process.append((query, q_hash))

    print(f"✅ {matched_count}/{len(songs_data)} songs verified. Skipping.")
    if to_process:
        print(f"🚀 {len(to_process)} songs to process.")
    print("-" * 40)

    if not to_process:
        print("✨ Sync complete!"); return

    # 4. PROCESS
    failed_set = set()
    if os.path.exists(failed_file):
        with open(failed_file, "r", encoding="utf-8") as f:
            failed_set = {line.strip() for line in f if line.strip()}

    pbar = tqdm(to_process, desc="📥 Progress", unit="song", dynamic_ncols=True)
    
    try:
        for query, q_hash in pbar:
            failed_set.discard(query)
            success = False
            for attempt in range(3):
                temp_path = None
                try:
                    s_name, a_name = query.split(" - ", 1) if " - " in query else (query, "")
                    
                    # --- NON-FATAL METADATA FETCH ---
                    data = None
                    try:
                        data = get_clean_metadata(s_name, a_name)
                    except Exception:
                        pass # Ignore network errors; save the song anyway

                    temp_path = download_song(query)
                    
                    if temp_path and os.path.exists(temp_path):
                        time.sleep(0.3)
                        base, ext = os.path.splitext(temp_path)
                        final_path = f"{base} [{q_hash}]{ext}"
                        
                        os.rename(temp_path, final_path)
                        
                        if data:
                            try: apply_metadata(final_path, data)
                            except: pass
                        
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
        print("\n\n🛑 Interrupted. Partial files will be cleaned on next run.")
    finally:
        with open(failed_file, "w", encoding="utf-8") as f:
            for item in sorted(failed_set): f.write(f"{item}\n")

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
                data = None
                try: data = get_clean_metadata(s, a)
                except: pass
                if data: apply_metadata(final, data)
        return

    run_from_csv(args.input)

if __name__ == "__main__":
    main()