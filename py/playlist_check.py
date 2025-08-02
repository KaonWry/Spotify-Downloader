from ytmusicapi import YTMusic
from downloader import fetch_spotify_data, get_info, search_song
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

ytm = YTMusic("browser.json")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        redirect_uri=os.getenv("REDIRECT_URI"),
        scope="playlist-read-private",
    )
)

youtube_playlist_id = "PLnfeFN03HObYCXIFH50zIMQTviUgkKGWb"
spotify_playlist_id = "1QYOoJynssmYto7yTYQ7eM"

results = fetch_spotify_data(sp, "playlist", spotify_playlist_id)
song_list = get_info("playlist", results)

song_id_list = []
for i, song in enumerate(song_list, start=1):
    search_result = search_song(song["title"], song["artist"], ytm)
    print(f"{i}/{len(song_list)}: {song['title']}-{song['artist']}: {search_result}")
    song_id_list.append(search_result)

playlist = ytm.get_playlist(youtube_playlist_id, limit = 9999)
tracks = playlist["tracks"]

youtube_video_id = [track["videoId"] for track in tracks if "videoId" in track]

missing = set(song_id_list) - set(youtube_video_id)

for id in missing:
    print(f"https://music.youtube.com/watch?v={id}")
