import requests
import os

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def get_liked_tracks(access_token):
    url = "https://api.spotify.com/v1/me/tracks?limit=50"
    headers = {"Authorization": f"Bearer {access_token}"}

    artists = set()
    while url:
        resp = requests.get(url, headers=headers).json()

        for item in resp["items"]:
            for artist in item["track"]["artists"]:
                artists.add(artist["id"])

        url = resp.get("next")

    return list(artists)


def follow_artists(access_token, artist_ids):
    url = "https://api.spotify.com/v1/me/following?type=artist"
    headers = {"Authorization": f"Bearer {access_token}"}
    chunks = [artist_ids[i:i+50] for i in range(0, len(artist_ids), 50)]

    for chunk in chunks:
        requests.put(url, headers=headers, json={"ids": chunk})


def main():
    print("Atualizando token…")
    access_token = get_access_token()

    print("Coletando músicas curtidas…")
    artists = get_liked_tracks(access_token)

    print(f"{len(artists)} artistas encontrados.")

    print("Seguindo artistas…")
    follow_artists(access_token, artists)

    print("Finalizado!")


if __name__ == "__main__":
    main()
