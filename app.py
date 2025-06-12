import os
import sys
from dotenv import load_dotenv
from urllib.parse import urlparse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TPE2, TALB, TDRC, TRCK


def parse_spotify_link(link):
    # Spotify URI format
    if link.startswith("spotify:"):
        parts = link.split(":")
        if len(parts) == 3:
            return {"type": parts[1], "id": parts[2]}

    # Spotify URL format
    elif "open.spotify.com" in link:
        parsed = urlparse(link)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 2:
            return {"type": path_parts[0], "id": path_parts[1]}

    return None


def fetch_spotify_data(type, id):
    try:
        if type == "playlist":
            result = sp.playlist_items(id)
        elif type == "album":
            result = sp.album(id)
        elif type == "track":
            result = sp.track(id)
        else:
            raise ValueError(f"Unsupported link type: {type}")
        return result
    except SpotifyException as e:
        print(
            f"Error: Unable to fetch {type} with ID {id}. It may be private, deleted, or invalid."
        )
        print(f"Details: {e}")
        sys.exit(1)


def get_info(type, result):
    track_list = []
    if type == "playlist":
        for item in result["items"]:
            track_info = {
                "title": item["track"]["name"],
                "artist": [artist["name"] for artist in item["track"]["artists"]],
                "album": item["track"]["album"]["name"],
                "album_cover": item["track"]["album"]["images"][0]["url"],
                "release": item["track"]["album"]["release_date"],
                "album_artist": [
                    artist["name"] for artist in item["track"]["album"]["artists"]
                ],
                "track_number": item["track"]["track_number"],
            }
            track_list.append(track_info)

    elif type == "album":
        for item in result["tracks"]["items"]:
            track_info = {
                "title": item["name"],
                "artist": [artist["name"] for artist in item["artists"]],
                "album": result["name"],
                "album_cover": result["images"][0]["url"],
                "release": result["release_date"],
                "album_artist": [artist["name"] for artist in result["artists"]],
                "track_number": item["track_number"],
            }
            track_list.append(track_info)

    elif type == "track":
        track_info = {
            "title": result["name"],
            "artist": [artist["name"] for artist in result["artists"]],
            "album": result["album"]["name"],
            "album_cover": result["album"]["images"][0]["url"],
            "release": result["album"]["release_date"],
            "album_artist": [artist["name"] for artist in result["album"]["artists"]],
            "track_number": result["track_number"],
        }
        track_list.append(track_info)

    return track_list


# Search for song with format "Title Artist1 Artist2...", returns song url
def search_song(title, artist):
    query = f"{title} {' '.join(artist)}"
    search_results = ytm.search(query, filter="songs")

    if not search_results:
        return None

    return f"https://music.youtube.com/watch?v={search_results[0]['videoId']}"


def embed_metadata(
    mp3_path, image_url, title, artist, album, release, album_artist, track_number
):
    audio = MP3(mp3_path, ID3=ID3)

    # Download image from Spotify
    response = requests.get(image_url)
    image_data = response.content

    # Embed song metadata
    audio.tags["TIT2"] = TIT2(encoding=3, text=title)  # Title
    audio.tags["TPE1"] = TPE1(encoding=3, text=", ".join(artist))  # Artist
    audio.tags["TPE2"] = TPE2(encoding=3, text=", ".join(album_artist))  # Album artist
    audio.tags["TALB"] = TALB(encoding=3, text=album)  # Album
    audio.tags["TDRC"] = TDRC(encoding=3, text=release.split("-")[0])  # Year of release
    audio.tags["TRCK"] = TRCK(encoding=3, text=str(track_number))  # Track number

    # Embed album cover
    audio.tags.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,  # Cover (front)
            desc="Cover",
            data=image_data,
        )
    )

    # Save changes
    audio.save(v2_version=3)


def sanitize_filename(name):
    return "".join(c for c in name if c not in r'<>:"/\|?*').strip()


if __name__ == "__main__":

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

    # Link input if no passed arguments
    if len(sys.argv) < 2:
        spotify_link = input("Paste Spotify URL/URI here: ").strip()
    else:
        spotify_link = sys.argv[1]

    playlist_info = parse_spotify_link(spotify_link)

    # Error handling for invalid link
    if not playlist_info:
        print("Error: Invalid Spotify link format.")
        sys.exit(1)
    results = fetch_spotify_data(
        playlist_info["type"], playlist_info["id"]
    )  # Raw API output
    song_list = get_info(playlist_info["type"], results)  # Processed song metadata
    os.system("cls" if os.name == "nt" else "clear")

    # Listing songs about to be and already downloaded
    download = []
    not_download = []
    for song in song_list:
        filename = f"{', '.join(song['artist'])} - {song['title']}"
        if os.path.exists(f"output/{sanitize_filename(filename)}.mp3"):
            not_download.append(filename)
        else:
            download.append(filename)
    print("Songs about to be downloaded:")
    for song in download:
        print(song)
    print("\nSongs not to be downloaded: ")
    for song in not_download:
        print(song)
    input("\nClick enter to continue...")

    # Create output directory if it doesn't exist yet
    os.makedirs("output", exist_ok=True)

    # Init ytmusicapi
    ytm = YTMusic()

    for i, song in enumerate(song_list, start=1):
        os.system("cls" if os.name == "nt" else "clear")
        print("Finished processing:")
        for j in range(i - 1):
            print(f'{', '.join(song_list[j]["artist"])} - {song_list[j]["title"]}')
        filename = f"{', '.join(song['artist'])} - {song['title']}"
        print(f"\nDownloading song: {filename} ({i}/{len(song_list)})")
        search_result = search_song(song["title"], song["artist"])
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"output/{sanitize_filename(filename)}.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "logtostderr": False,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        if os.path.exists(f"output/{sanitize_filename(filename)}.mp3"):
            print(
                f"File exists: {f'{sanitize_filename(filename)}.mp3'} — Skipping download, updating metadata..."
            )
        else:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_result])

        embed_metadata(
            f"output/{sanitize_filename(filename)}.mp3",
            song["album_cover"],
            song["title"],
            song["artist"],
            song["album"],
            song["release"],
            song["album_artist"],
            song["track_number"],
        )
