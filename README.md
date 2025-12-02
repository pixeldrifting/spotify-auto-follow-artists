Spotify AutoFollow

Segue automaticamente todos os artistas das músicas curtidas.

Como usar
1. Obtenha:

SPOTIFY_CLIENT_ID

SPOTIFY_CLIENT_SECRET

SPOTIFY_REFRESH_TOKEN

2. Adicione ao GitHub

No repositório:

Settings → Secrets and variables → Actions → New repository secret

Crie:

SPOTIFY_CLIENT_ID

SPOTIFY_CLIENT_SECRET

SPOTIFY_REFRESH_TOKEN

3. Execução manual

O script só roda quando você quiser, usando:

Actions → Auto Follow Artists → Run workflow

Sempre que rodar, ele:

Gera um access token automaticamente usando o refresh token

Lê suas músicas curtidas

Segue todos os artistas novos
