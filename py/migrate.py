from downloader import parse_spotify_link, fetch_spotify_data, get_info, search_song
import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic


if __name__ == "__main__":
    # Load credentials
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
    sp = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=os.getenv("CLIENT_ID"),
            client_secret=os.getenv("CLIENT_SECRET"),
            redirect_uri=os.getenv("REDIRECT_URI"),
            scope="playlist-read-private",
        )
    )

    # Manually input Spotify link if no argument passed
    if len(sys.argv) < 2:
        spotify_link = input("Paste Spotify URL/URI here: ").strip()
    else:
        spotify_link = sys.argv[1]

    playlist_info = parse_spotify_link(spotify_link)

    # Error handling for invalid link
    if not playlist_info:
        print("Error: Invalid Spotify link format.")
        sys.exit(1)

    # Raw API output
    results = fetch_spotify_data(sp, playlist_info["type"], playlist_info["id"])

    # Processed song metadata
    song_list = get_info(playlist_info["type"], results)

    ytm = YTMusic()

    for i, song in enumerate(song_list, start=1):
        search_result = search_song(song["title"], song["artist"], ytm)
        print(f"{song['title']}-{song['artist']}: {search_result}")
