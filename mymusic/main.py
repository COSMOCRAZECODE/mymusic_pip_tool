import os
import csv
import argparse
from tqdm import tqdm
from .downloader import download_song
from .metadata_fetcher import get_clean_metadata
from .tagger import apply_metadata

def run_from_csv(csv_file):
    """Main execution logic for processing the CSV file."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 1. Setup Backup Folder and History
    backup_dir = "backup"
    history_file = os.path.join(backup_dir, "downloaded_history.txt")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    downloaded_history = []
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as h:
            downloaded_history = [line.strip() for line in h.readlines()]

    # 2. Check for playlist.csv and provide instructions if missing
    if not os.path.exists(csv_file):
        print("🎵 PRO MUSIC PIPELINE (Exportify Edition)")
        print("-" * 40)
        print(f"❌ Error: '{csv_file}' not found in this folder!")
        print("\n📝 HOW TO GET YOUR TRACKLIST:")
        print("1. Go to: https://watsonbox.github.io/exportify/")
        print("2. Log in and find your playlist.")
        print("3. Click 'Export'. It will download a CSV file.")
        print(f"4. Move that file here and rename it to '{csv_file}'.")
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

    if not songs:
        print("❌ Error: No songs found in the CSV. Check the file format.")
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
                
        except Exception:
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
    
    args = parser.parse_args()
    run_from_csv(args.input)

if __name__ == "__main__":
    if not os.path.exists('downloads'): 
        os.makedirs('downloads')
    main()