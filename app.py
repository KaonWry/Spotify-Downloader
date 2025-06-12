import spotipy
from spotipy.oauth2 import SpotifyOAuth
from urllib.parse import urlparse
import sys
from dotenv import load_dotenv
import os

 
if len(sys.argv) < 2:
    print("Usage: python app.py <spotify_link>")
    sys.exit(1)

spotify_link = sys.argv[1]

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri=os.getenv("REDIRECT_URI"),
    scope="playlist-read-private"
))

def parse_spotify_link(link):
    if link.startswith("spotify:"):
        # Spotify URI format
        parts = link.split(":")
        if len(parts) == 3:
            return {"type": parts[1], "id": parts[2]}
    
    elif "open.spotify.com" in link:
        # Spotify URL format
        parsed = urlparse(link)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 2:
            return {"type": path_parts[0], "id": path_parts[1]}
    
    return None

playlist_info = parse_spotify_link(spotify_link)

def fetch_spotify_data(type, id):
    if type == "playlist":
        result = sp.playlist_items(id)  # get tracks from playlist
    elif type == "album":
        result = sp.album_tracks(id)   # get tracks from album
    elif type == "track":
        result = sp.track(id)          # single track metadata
    else:
        raise ValueError(f"Unsupported link type: {type}")

    return result

results = fetch_spotify_data(playlist_info["type"], playlist_info["id"])

def get_info(type, result):
    print(f"Type: {type}")
    print(f"ID: {playlist_info['id']}")
    if type == 'playlist':
        for item in result['items']:
            title = item['track']['name']
            artist = item["track"]["artists"][0]['name']
            print(f"{artist} - {title}")
            
    elif type == 'album':
        for item in result['items']:
            title = item['name']
            artist = item['artists'][0]['name']
            print(f"{artist} - {title}")
            
    elif type == 'track':
        title = result['name']
        artist = result['artists'][0]['name']
        print(f"{artist} - {title}")
        
get_info(playlist_info['type'], results)