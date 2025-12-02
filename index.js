import fetch from 'node-fetch';

const clientId = process.env.SPOTIFY_CLIENT_ID;
const clientSecret = process.env.SPOTIFY_CLIENT_SECRET;
const refreshToken = process.env.SPOTIFY_REFRESH_TOKEN;

async function refreshAccessToken() {
  const params = new URLSearchParams();
  params.append("grant_type", "refresh_token");
  params.append("refresh_token", refreshToken);

  const authHeader = Buffer.from(`${clientId}:${clientSecret}`).toString("base64");

  const response = await fetch("https://accounts.spotify.com/api/token", {
    method: "POST",
    headers: {
      Authorization: `Basic ${authHeader}`,
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: params
  });

  const data = await response.json();

  if (!response.ok) {
    console.error("Erro ao atualizar token:", data);
    throw new Error("Falha ao gerar access token");
  }

  return data.access_token;
}

async function autofollow() {
  const accessToken = await refreshAccessToken();

  // IDS dos artistas que você quer seguir
  const artists = [
    "4NHQUGzhtTLFvgF5SZesLK",
    "1uNFoZAHBGtllmzznpCI3s"
  ];

  for (const id of artists) {
    const url = `https://api.spotify.com/v1/me/following?type=artist&ids=${id}`;
    const res = await fetch(url, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (res.status === 204) {
      console.log(`✔ Seguido: ${id}`);
    } else {
      const error = await res.text();
      console.log(`❌ Erro ao seguir ${id}: ${error}`);
    }
  }
}

autofollow().catch(err => {
  console.error("Erro fatal:", err);
  process.exit(1);
});
