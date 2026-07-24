import os
import requests

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"


def get_access_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Falha ao atualizar token ({response.status_code}): {response.text}"
        )

    return response.json()["access_token"]


def spotify_get(access_token, url):
    response = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Erro ao acessar Spotify ({response.status_code}): {response.text}"
        )

    return response.json()


def get_current_user(access_token):
    return spotify_get(access_token, f"{API_BASE}/me")


def get_liked_tracks(access_token):
    liked_tracks = {}
    url = f"{API_BASE}/me/tracks?limit=50"

    while url:
        data = spotify_get(access_token, url)

        for item in data.get("items", []):
            track = item.get("track")
            if not track or not track.get("id"):
                continue
            liked_tracks[track["id"]] = track

        url = data.get("next")

    return liked_tracks


def get_user_playlists(access_token, user_id):
    playlists = []
    url = f"{API_BASE}/me/playlists?limit=50"

    while url:
        data = spotify_get(access_token, url)

        for playlist in data.get("items", []):
            owner = playlist.get("owner", {})
            if owner.get("id") != user_id:
                continue

            playlists.append(
                {
                    "id": playlist["id"],
                    "name": playlist["name"],
                }
            )

        url = data.get("next")

    return playlists


def get_playlist_track_ids(access_token, playlist_id):
    track_ids = set()
    url = f"{API_BASE}/playlists/{playlist_id}/tracks?limit=100"

    while url:
        data = spotify_get(access_token, url)

        for item in data.get("items", []):
            track = item.get("track")
            if track and track.get("id"):
                track_ids.add(track["id"])

        url = data.get("next")

    return track_ids


def find_orphan_tracks(liked_tracks, playlist_track_ids):
    return {
        track_id: track
        for track_id, track in liked_tracks.items()
        if track_id not in playlist_track_ids
    }


def main():
    print("=== Spotify - Órfãs ===\n")

    access_token = get_access_token()
    user = get_current_user(access_token)

    print(f"Usuário: {user['display_name']}\n")

    liked_tracks = get_liked_tracks(access_token)
    print(f"Músicas curtidas: {len(liked_tracks)}")

    playlists = get_user_playlists(access_token, user["id"])
    print(f"Playlists próprias: {len(playlists)}")

    playlist_track_ids = set()

    for playlist in playlists:
        print(f"Lendo: {playlist['name']}")
        playlist_track_ids.update(
            get_playlist_track_ids(access_token, playlist["id"])
        )

    print(f"\nMúsicas presentes nas suas playlists: {len(playlist_track_ids)}")

    orphan_tracks = find_orphan_tracks(
        liked_tracks,
        playlist_track_ids,
    )

    print(f"Músicas órfãs: {len(orphan_tracks)}\n")

    for track in sorted(
        orphan_tracks.values(),
        key=lambda t: (t["artists"][0]["name"], t["name"])
    ):
        artists = ", ".join(a["name"] for a in track["artists"])
        print(f"- {track['name']} — {artists}")


if __name__ == "__main__":
    main()
