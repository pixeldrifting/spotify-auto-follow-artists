import os
import requests
from time import sleep

# Espera variáveis de ambiente com estes nomes (defina nos GitHub Secrets):
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE = "https://api.spotify.com/v1"

def get_access_token():
    """
    Troca refresh_token por access_token.
    Usa HTTP Basic Auth (client_id:client_secret) — método compatível e confiável.
    """
    if not CLIENT_ID or not CLIENT_SECRET or not REFRESH_TOKEN:
        raise RuntimeError("As variáveis de ambiente SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET e SPOTIFY_REFRESH_TOKEN devem estar definidas.")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }
    # usa auth em vez de enviar client_secret no corpo
    resp = requests.post(TOKEN_URL, data=data, auth=(CLIENT_ID, CLIENT_SECRET), timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Falha ao atualizar token ({resp.status_code}): {resp.text}")
    return resp.json()["access_token"]

def get_liked_tracks(access_token):
    url = f"{API_BASE}/me/tracks?limit=50"
    headers = {"Authorization": f"Bearer {access_token}"}
    artists = set()

    while url:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Erro ao buscar músicas curtidas ({resp.status_code}): {resp.text}")
        data = resp.json()
        for item in data.get("items", []):
            track = item.get("track")
            if not track:
                continue
            for artist in track.get("artists", []):
                if artist.get("id"):
                    artists.add(artist["id"])
        url = data.get("next")  # próxima página (ou None)
        # pequeno atraso para não sobrecarregar
        sleep(0.2)

    return list(artists)

def follow_artists(access_token, artist_ids):
    url = f"{API_BASE}/me/following?type=artist"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Spotify aceita até 50 ids por request
    chunks = [artist_ids[i:i+50] for i in range(0, len(artist_ids), 50)]
    for chunk in chunks:
        resp = requests.put(url, headers=headers, json={"ids": chunk})
        if resp.status_code not in (204, 200):
            # 204 = sucesso sem corpo
            raise RuntimeError(f"Erro ao seguir artistas ({resp.status_code}): {resp.text}")
        sleep(0.2)

def main():
    print("Atualizando token…")
    access_token = get_access_token()

    print("Coletando músicas curtidas…")
    artists = get_liked_tracks(access_token)
    print(f"{len(artists)} artistas encontrados.")

    if not artists:
        print("Nenhum artista novo para seguir.")
        return

    print("Seguindo artistas…")
    follow_artists(access_token, artists)
    print("Finalizado!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Erro:", e)
        raise
