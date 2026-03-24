from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER
from tqdm import tqdm

def apply_metadata(file_path, metadata):
    try:
        # Load existing ID3 tags or create a new object if none exist
        try:
            audio = ID3(file_path)
        except Exception:
            audio = ID3()

        # Add metadata frames
        # TIT2: Title, TPE1: Artist, TALB: Album, TYER: Year
        audio.add(TIT2(encoding=3, text=metadata['title']))
        audio.add(TPE1(encoding=3, text=metadata['artist']))
        audio.add(TALB(encoding=3, text=metadata['album']))
        audio.add(TYER(encoding=3, text=str(metadata['date'])))
        
        audio.save(file_path)
        
        # Use tqdm.write instead of print to keep the progress bar at the bottom
        # tqdm.write(f"✨ Metadata stitched into: {file_path}")
        
    except Exception as e:
        tqdm.write(f"⚠️ Tagging error for {file_path}: {e}")