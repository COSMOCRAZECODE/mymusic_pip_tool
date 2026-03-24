import musicbrainzngs
from tqdm import tqdm

def get_clean_metadata(song_name, artist_name):
    # MusicBrainz requires a useragent to identify the request source
    musicbrainzngs.set_useragent("MyCoolDownloader", "0.1", "contact@example.com")
    
    try:
        # We limit to 1 to get the most relevant match quickly
        search_results = musicbrainzngs.search_recordings(query=song_name, artist=artist_name, limit=1)
        
        if search_results.get('recording-list'):
            recording = search_results['recording-list'][0]
            
            # Extracting release information
            release_list = recording.get('release-list', [])
            album_name = release_list[0]['title'] if release_list else "Unknown Album"
            
            # Get the year (first 4 characters of the date)
            release_date = "2026"
            if release_list and 'date' in release_list[0]:
                release_date = release_list[0]['date'][:4]
            
            return {
                "title": recording['title'],
                "artist": recording['artist-credit-phrase'],
                "album": album_name,
                "date": release_date
            }
            
    except Exception as e:
        # Use tqdm.write instead of print to avoid breaking the progress bar UI
        tqdm.write(f"⚠️ Metadata error for {song_name}: {e}")
        
    return None