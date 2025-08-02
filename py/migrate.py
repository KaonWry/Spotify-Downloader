from downloader import parse_spotify_link, fetch_spotify_data, get_info, search_song
import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic
import argparse

if __name__ == "__main__":
    # CLI Argument parsing
    parser = argparse.ArgumentParser(
        description="Migrate a Spotify playlist to YouTube Music"
    )
    parser.add_argument("spotify_link", help="Spotify playlist URL or URI")
    parser.add_argument("playlist_name", help="Name of the new YouTube playlist")
    args = parser.parse_args()
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
    # Extract Spotify playlist info
    playlist_info = parse_spotify_link(args.spotify_link)
    if not playlist_info:
        print("Error: Invalid Spotify link format.")
        sys.exit(1)

    # Raw API output
    results = fetch_spotify_data(sp, playlist_info["type"], playlist_info["id"])
    print(len(results["items"]))

    # Processed song metadata
    song_list = get_info(playlist_info["type"], results)
    print(len(song_list))

    ytm = YTMusic("browser.json")
    song_id_list = []
    for i, song in enumerate(song_list, start=1):
        search_result = search_song(song["title"], song["artist"], ytm)
        print(f"{i}/{len(song_list)}: {song['title']}-{song['artist']}: {search_result}")
        song_id_list.append(search_result)
    print(len(song_id_list))

    playlist_id = ytm.create_playlist(
        args.playlist_name, "Migrated Spotify Playlist", "PUBLIC", song_id_list
    )
    print(playlist_id)
