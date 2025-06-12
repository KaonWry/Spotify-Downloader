import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic


# Init ytmusicapi
ytm = YTMusic()

# Link input
if len(sys.argv) < 2:
    spotify_link = input("Paste Spotify URL/URI here: ").strip()
else:
    spotify_link = sys.argv[1]

# Load credentials
load_dotenv()
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        scope="playlist-read-private",
    )
)


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
        result = sp.playlist_items(id)  # Playlist
    elif type == "album":
        result = sp.album(id)  # Album
    elif type == "track":
        result = sp.track(id)  # Single track
    else:
        raise ValueError(f"Unsupported link type: {type}")

    return result


results = fetch_spotify_data(playlist_info["type"], playlist_info["id"])


# Get song info
def get_info(type, result):
    track_list = []
    if type == "playlist":
        for item in result["items"]:
            track_info = {
                "title": item["track"]["name"],
                "artist": [artist["name"] for artist in item["track"]["artists"]],
                "duration_ms": item["track"]["duration_ms"],
                "album": item["track"]["album"]["name"],
                "album_cover": item["track"]["album"]["images"][0]["url"],
            }
            track_list.append(track_info)

    elif type == "album":
        for item in result["tracks"]["items"]:
            track_info = {
                "title": item["name"],
                "artist": [artist["name"] for artist in item["artists"]],
                "duration_ms": item["duration_ms"],
                "album": result["name"],
                "album_cover": result["images"][0]["url"],
            }
            track_list.append(track_info)

    elif type == "track":
        track_info = {
            "title": result["name"],
            "artist": [artist["name"] for artist in result["artists"]],
            "duration_ms": result["duration_ms"],
            "album": result["album"]["name"],
            "album_cover": result["album"]["images"][0]["url"],
        }
        track_list.append(track_info)

    return track_list


song_list = get_info(playlist_info["type"], results)


def search_song(title, artist):
    query = f"{title} {' '.join(artist)}"
    search_results = ytm.search(query, filter="songs")

    if not search_results:
        return None

    best_match = search_results[0]
    return f"https://music.youtube.com/watch?v={best_match['videoId']}"


for song in song_list:
    search_result = search_song(song["title"], song["artist"])
    print(search_result)
