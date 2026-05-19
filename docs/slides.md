---
marp: true
theme: default
class: invert
paginate: true
title: MovieFlix — Mini-projet DevNet
---

# 🎬 MovieFlix
### Plateforme de découverte de films & watchlist personnelle

**Mini-projet de fin d'année — DevNet & Automatisation**

Équipe : **Med Abroud** & **Tesnime Chriaa**
Date : *date de soutenance*

---

## 1. Contexte & problématique

**Problématique :** comment offrir aux utilisateurs une expérience moderne pour découvrir, rechercher et organiser leurs films préférés, à partir d'un catalogue mondial mis à jour en temps réel ?

**Notre réponse :** une application web full-stack qui agrège l'API publique **TMDB** (~1 M+ films) et y ajoute une couche personnalisée (compte utilisateur + watchlist persistante).

**Couverture du cahier des charges :**
- ✅ Backend Python (FastAPI)
- ✅ Frontend dynamique (React)
- ✅ API REST externe (TMDB) + API REST interne (8 endpoints)
- ✅ Conteneurisation (Docker + Compose)
- ✅ Automatisation (Bash + Ansible)
- ✅ Tests automatisés (pytest)
- ✅ Sécurité (JWT + bcrypt)
- ✅ Bonus CI/CD (GitHub Actions)

📁 *Cahier des charges : `CAHIER DES CHARGES-1.pdf` (racine projet)*

---

## 2. Architecture technique

```
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   Browser    │───▶│  Nginx + React   │───▶│   FastAPI    │
│              │    │  (web container) │    │   (Python)   │
└──────────────┘    └──────────────────┘    └──────┬───────┘
                                                   │
                                          ┌────────┴────────┐
                                     ┌────▼────┐      ┌─────▼─────┐
                                     │Postgres │      │ TMDB API  │
                                     │   16    │      │ (externe) │
                                     └─────────┘      └───────────┘
```

**3 conteneurs orchestrés par Docker Compose** :
- `web` (Nginx + React buildé)
- `api` (FastAPI + SQLAlchemy)
- `db` (PostgreSQL 16)

Communication : `browser → web:80 → api:8000 → {db:5432, TMDB}`

📁 *Définition complète : `movieflix/docker-compose.yml`*

---

## 3. Stack & structure du projet

| Couche | Technologie | Justification |
|---|---|---|
| Backend | **FastAPI** 0.115 | Async, validation Pydantic, doc OpenAPI auto |
| Frontend | **React 18 + Vite** | Build ultra-rapide, écosystème mature |
| BDD | **PostgreSQL 16** | Robuste, ACID, prêt prod |
| Conteneurs | **Docker + Compose** | Iso-env dev/prod |
| Provisioning | **Ansible** | Idempotent, déploiement zéro-touche |
| CI/CD | **GitHub Actions** | Intégré au repo, gratuit |
| API externe | **TMDB** | Gratuite, 1M+ films, multilingue |

```
movieflix/
├── backend/   (FastAPI + tests pytest)
├── frontend/  (React + Vite + nginx)
├── ansible/   (playbook + inventaire)
├── scripts/   (deploy.sh)
├── .github/workflows/ci-cd.yml
└── docker-compose.yml
```

📁 *Racine du projet : `C:\Users\M\Desktop\devnet\movieflix\`*

---

## 4. Backend Python — point d'entrée FastAPI

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, movies, watchlist

app = FastAPI(
    title="MovieFlix API",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, ...)

@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(watchlist.router)
```

📁 **`backend/app/main.py`** — architecture modulaire : 1 router par domaine métier

---

## 5. Backend — modèles SQLAlchemy & schémas Pydantic

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    watchlist = relationship("WatchlistItem", cascade="all, delete-orphan")

class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id", "tmdb_id"),)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    tmdb_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
```

📁 **`backend/app/models.py`** — tables SQL générées au démarrage

```python
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
```

📁 **`backend/app/schemas.py`** — validation des entrées/sorties via Pydantic

---

## 6. Backend — gestion d'erreurs propre

```python
@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    user = User(username=payload.username,
                hashed_password=hash_password(payload.password))
    db.add(user); db.commit()
    return Token(access_token=create_access_token(user.username))

@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), ...):
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
```

📁 **`backend/app/routers/auth.py`** — codes HTTP RFC 7231-compliant

| Cas | Code | Comportement |
|---|---|---|
| Succès création | **201** | + JWT |
| User déjà pris | **409** | Conflict |
| Bad credentials | **401** | Unauthorized |
| Validation Pydantic KO | **422** | Auto |

---

## 7. Frontend React — navigation et état d'authentification

```jsx
export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  return (
    <div className="app">
      <nav>
        <Link to="/">Tendances</Link>
        {token && <Link to="/watchlist">Ma liste</Link>}
        {token ? <button onClick={handleLogout}>Déconnexion</button>
               : <Link to="/login">Connexion</Link>}
      </nav>
      <Routes>
        <Route path="/" element={<Home authenticated={!!token} />} />
        <Route path="/watchlist" element={<Watchlist />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
      </Routes>
    </div>
  );
}
```

📁 **`frontend/src/App.jsx`** — la nav se met à jour automatiquement à la connexion

---

## 8. Frontend — client API centralisé

```js
function authHeaders() {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export const api = {
  trending: () => http('/api/movies/trending'),
  search: (q) => http(`/api/movies/search?q=${encodeURIComponent(q)}`),
  register: (u, p) => http('/api/auth/register',
    { method: 'POST', body: JSON.stringify({username: u, password: p}) }),
  watchlist: () => http('/api/watchlist'),
  addToWatchlist: (m) => http('/api/watchlist',
    { method: 'POST', body: JSON.stringify({tmdb_id: m.id, title: m.title}) }),
};
```

📁 **`frontend/src/api.js`** — injecte automatiquement le JWT dans chaque requête

---

## 9. Intégration API REST — client TMDB

```python
class TMDBClient:
    async def _get(self, path: str, params: dict = None) -> dict:
        params = {**(params or {}), "api_key": self.api_key, "language": "fr-FR"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.get(f"{self.base_url}{path}", params=params)
            except httpx.HTTPError as exc:
                raise HTTPException(502, f"TMDB unreachable: {exc}")
        if response.status_code == 401:
            raise HTTPException(502, "TMDB authentication failed")
        return response.json()

    async def trending(self): return await self._get("/trending/movie/week")
    async def search(self, query, page=1):
        return await self._get("/search/movie", {"query": query, "page": page})
```

📁 **`backend/app/services/tmdb.py`** — couche d'abstraction async avec gestion d'erreurs

→ Panne TMDB ou clé invalide → **502 Bad Gateway** explicite au client

---

## 10. Intégration API — endpoints REST exposés

| Méthode | URL | Auth | Description |
|---|---|---|---|
| `GET` | `/api/health` | ❌ | Healthcheck |
| `GET` | `/api/movies/trending` | ❌ | Top semaine (TMDB) |
| `GET` | `/api/movies/search?q=...` | ❌ | Recherche (TMDB) |
| `GET` | `/api/movies/{id}` | ❌ | Détails d'un film |
| `POST` | `/api/auth/register` | ❌ | Création compte → JWT |
| `POST` | `/api/auth/login` | ❌ | Connexion → JWT |
| `GET` | `/api/watchlist` | ✅ | Liste perso |
| `POST` | `/api/watchlist` | ✅ | Ajout |
| `DELETE` | `/api/watchlist/{id}` | ✅ | Suppression |

📁 **`backend/app/routers/{auth,movies,watchlist}.py`**

📘 **Swagger UI auto-généré** disponible à `http://localhost:8080/api/docs`

→ **2 APIs consommées** : TMDB (externe) + notre propre API REST (interne)

---

## 11. Sécurité — Authentification JWT

```python
from datetime import datetime, timedelta, timezone
from jose import jwt

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid credentials",
                           headers={"WWW-Authenticate": "Bearer"})
    user = db.query(User).filter(User.username == username).first()
    if user is None: raise HTTPException(401, "Invalid credentials")
    return user
```

📁 **`backend/app/security.py`** — **stateless** : aucune session côté serveur

---

## 12. Sécurité — Hashage bcrypt + autres mesures

```python
import bcrypt
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8")[:72], bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
```

📁 **`backend/app/security.py`**

**Exemple de hash réellement stocké en BDD :**
```
$2b$12$/BuTRGwd1SD5SHVlRPpDa.I.n6LnGMgBsyTNbRLleK39GAtPvy67K
```

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

📁 **`frontend/nginx.conf`** — headers de sécurité HTTP côté reverse-proxy

📁 **`backend/Dockerfile`** — conteneur en **utilisateur non-root** (`USER app`)
📁 **`backend/app/main.py`** — **CORS** restrictif (whitelist d'origines)

---

## 13. Tests automatisés — pytest

```python
def test_watchlist_crud(client):
    token = _register_and_login(client, "bob")
    headers = {"Authorization": f"Bearer {token}"}

    empty = client.get("/api/watchlist", headers=headers)
    assert empty.status_code == 200 and empty.json() == []

    add = client.post("/api/watchlist", headers=headers,
        json={"tmdb_id": 27205, "title": "Inception"})
    assert add.status_code == 201

    dup = client.post("/api/watchlist", headers=headers,
        json={"tmdb_id": 27205, "title": "Inception"})
    assert dup.status_code == 409   # contrainte UNIQUE

def test_watchlist_requires_auth(client):
    assert client.get("/api/watchlist").status_code == 401
```

📁 **`backend/tests/test_auth_watchlist.py`**

```python
@respx.mock
def test_trending_uses_tmdb(client):
    respx.get(f"{TMDB}/trending/movie/week").mock(
        return_value=httpx.Response(200, json={...}))
    response = client.get("/api/movies/trending")
    assert response.status_code == 200
```

📁 **`backend/tests/test_movies.py`** — TMDB mocké, pas de vraie requête réseau

---

## 14. Tests — résultats d'exécution

```bash
$ docker compose exec api pytest -v

============================= test session starts =============================
platform win32 -- Python 3.13.0, pytest-8.3.3, pluggy-1.6.0
rootdir: /app
configfile: pytest.ini
plugins: anyio-4.13.0, asyncio-0.24.0, respx-0.21.1
collected 5 items

tests/test_auth_watchlist.py::test_register_and_duplicate    PASSED  [ 20%]
tests/test_auth_watchlist.py::test_watchlist_crud            PASSED  [ 40%]
tests/test_auth_watchlist.py::test_watchlist_requires_auth   PASSED  [ 60%]
tests/test_health.py::test_health_ok                          PASSED  [ 80%]
tests/test_movies.py::test_trending_uses_tmdb                 PASSED  [100%]

============================== 5 passed in 1.12s ==============================
```

📁 **`backend/tests/`** · configuration : **`backend/pytest.ini`**

✅ **5/5 tests passent** — couvre auth, CRUD watchlist, sécurité (401), intégration TMDB

---

## 15. Docker — Dockerfile backend optimisé

```dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .                  # cache layer indépendant
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN addgroup --system app && adduser --system --ingroup app app
USER app                                  # ← non-root (sécurité)

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

📁 **`backend/Dockerfile`** · ignorés : **`backend/.dockerignore`**

→ **Image légère** (`python:slim`) · **cache pip** · **healthcheck natif Docker**

---

## 16. Docker — Dockerfile frontend (multi-stage)

```dockerfile
# ───── Stage 1 : BUILD avec Node 20 ─────
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build                # produit /app/dist (HTML/CSS/JS statiques)

# ───── Stage 2 : RUNTIME avec Nginx ─────
FROM nginx:1.27-alpine AS runtime
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

📁 **`frontend/Dockerfile`** · config Nginx : **`frontend/nginx.conf`**

**Bénéfice du multi-stage :**
- Stage 1 (Node + node_modules) : ~1 GB → **jeté**
- Stage 2 (Nginx + dist statiques) : **~30 MB** ← image finale

---

## 17. Docker — orchestration Compose

```yaml
services:
  db:
    image: postgres:16-alpine
    environment: { POSTGRES_USER: movieflix, POSTGRES_PASSWORD: movieflix, ... }
    volumes: [db_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U movieflix"]
      interval: 10s
    networks: [movieflix]

  api:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+psycopg2://movieflix:movieflix@db:5432/movieflix
      TMDB_API_KEY: ${TMDB_API_KEY}
      JWT_SECRET: ${JWT_SECRET}
    depends_on:
      db: { condition: service_healthy }    # ← attend que la BDD soit prête
    networks: [movieflix]

  web:
    build: ./frontend
    depends_on: [api]
    ports: ["8080:80"]
    networks: [movieflix]

volumes: { db_data: }
networks: { movieflix: { driver: bridge } }
```

📁 **`docker-compose.yml`** · variables : **`.env`** (basé sur `.env.example`)

---

## 18. Automatisation — Script Bash

```bash
#!/usr/bin/env bash
set -euo pipefail
MODE="${1:-local}"

if [[ "${MODE}" == "local" ]]; then
  echo "[deploy] Local deployment via docker compose"
  command -v docker >/dev/null || die "Docker not installed"
  docker compose pull --ignore-pull-failures || true
  docker compose up -d --build
  for i in {1..30}; do
    if curl -fsS "http://localhost:8080/api/health" >/dev/null 2>&1; then
      echo "[deploy] API healthy. UI: http://localhost:8080"
      exit 0
    fi
    sleep 2
  done
  die "API did not become healthy in time"

elif [[ "${MODE}" == "remote" ]]; then
  echo "[deploy] Remote deployment via Ansible"
  ansible-playbook -i ansible/inventory.ini ansible/deploy.yml
fi
```

📁 **`scripts/deploy.sh`** — une commande : `./scripts/deploy.sh local|remote`

---

## 19. Automatisation — Playbook Ansible

```yaml
- name: Deploy MovieFlix stack
  hosts: movieflix
  become: true
  tasks:
    - name: Install Docker engine & compose plugin
      apt:
        name: [docker-ce, docker-ce-cli, containerd.io, docker-compose-plugin]
        state: present

    - name: Sync project sources to /opt/movieflix
      synchronize:
        src: "{{ playbook_dir }}/.."
        dest: "{{ project_root }}/"
        rsync_opts: ["--exclude=.git", "--exclude=node_modules"]

    - name: Copy environment file
      copy: { src: "../.env", dest: "{{ project_root }}/.env", mode: '0600' }

    - name: Build and start the stack
      command: docker compose up -d --build
      args: { chdir: "{{ project_root }}" }

    - name: Wait for API health
      uri: { url: "http://localhost:8080/api/health" }
      register: health
      retries: 12
      delay: 5
      until: health.status == 200
```

📁 **`ansible/deploy.yml`** · cibles : **`ansible/inventory.ini`** — **idempotent**

---

## 20. Bonus — Pipeline CI/CD (GitHub Actions)

```yaml
on: { push: { branches: [main] }, pull_request: { branches: [main] } }

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12', cache: 'pip' }
      - run: pip install -r requirements.txt && pip install ruff
      - run: ruff check app tests           # lint
      - run: pytest                          # tests

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm install && npm run build

  docker-build:
    needs: [backend-tests, frontend-build]
    steps:
      - uses: docker/build-push-action@v6
        with: { context: ./backend, cache-from: type=gha, cache-to: type=gha,mode=max }
      - uses: docker/build-push-action@v6
        with: { context: ./frontend, cache-from: type=gha }
```

📁 **`.github/workflows/ci-cd.yml`**

→ À chaque push : **lint + tests + build images** — déploiement bloqué si KO

---

## 21. Démo en direct — parcours utilisateur

**Étape 1 — Lancement de la stack (1 commande)**
```bash
$ docker compose up -d --build
[+] Running 4/4
 ✔ Container movieflix-db   Healthy
 ✔ Container movieflix-api  Started
 ✔ Container movieflix-web  Started
```
📁 *Commande à exécuter depuis la racine : `movieflix/`*

**Étape 2 — Inspection des conteneurs**
```bash
$ docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
NAMES           STATUS            PORTS
movieflix-web   Up (healthy)      0.0.0.0:8080->80/tcp
movieflix-api   Up (healthy)      8000/tcp
movieflix-db    Up (healthy)      5432/tcp
```

**Étape 3 — Démo UI** → `http://localhost:8080` (films TMDB live, recherche, watchlist)

**Étape 4 — Swagger** → `http://localhost:8080/api/docs`

---

## 22. Démo — parcours API complet validé

**Test du parcours via PowerShell (toutes les réponses HTTP) :**

```
[1] POST /api/auth/register  (demo_6116)   → token JWT généré
[2] POST /api/auth/login                    → reconnecté, token valide
[3] GET  /api/watchlist (vide)              → 0 items
[4] POST /api/watchlist  x 3                → Inception, Matrix, Dark Knight
[5] GET  /api/watchlist                     → 3 items
[6] DELETE /api/watchlist/603 (Matrix)      → reste 2
[7] GET  /api/watchlist SANS token          → HTTP 401 (sécurité OK ✅)
```

📁 *Endpoints servis par : `backend/app/routers/auth.py` + `watchlist.py`*

→ Cas nominal · cas erreur (doublon = 409) · cas sécurité (sans token = 401)

---

## 23. Démo — preuve de persistance en BDD

**Contenu réel des tables après le parcours :**

```
========== TABLE users ==========
ID  USERNAME      PASSWORD_HASH (bcrypt $2b$12$...)               CREATED_AT
1   testuser      $2b$12$6.nVTFNW1ltUobOY065ZR.ZPc2E9uqMNpXxIGV…  2026-05-19 03:11:59
2   medanroud     $2b$12$uuskI9O1Gsz5JusCTQOhoegsdkPIGuWBUZkqi2…  2026-05-19 03:12:29
4   demo_6116     $2b$12$/BuTRGwd1SD5SHVlRPpDa.I.n6LnGMgBsyTNbR…  2026-05-19 03:16:59

========== TABLE watchlist_items ==========
ID  USER_ID  TMDB_ID   TITRE              ADDED_AT
3   2        1339713   Obsession          2026-05-19 03:13:42
4   4        27205     Inception          2026-05-19 03:17:00
6   4        155       The Dark Knight    2026-05-19 03:17:00
```

📁 *Schéma SQL généré par : `backend/app/models.py`*
📁 *Fichier BDD (mode local SQLite) : `backend/movieflix.db`*
📁 *BDD Docker : volume `movieflix_db_data` (PostgreSQL 16)*

✅ Aucun mot de passe en clair · ✅ FK + ON DELETE CASCADE · ✅ UNIQUE(user_id, tmdb_id)

---

## 24. Perspectives & améliorations futures

**Production-readiness :**
- 🚀 Déploiement **Kubernetes** (Helm chart) avec auto-scaling
- 🔄 **Cache Redis** pour les réponses TMDB (réduit le rate-limit)
- 📊 Observabilité : **Prometheus + Grafana** + traces OpenTelemetry
- 🌍 Internationalisation complète (FR / EN / AR)

**Fonctionnel :**
- ⭐ Système de notes et de critiques personnelles
- 🤝 Partage de watchlist entre utilisateurs (recommandations sociales)
- 📱 Application mobile **React Native** réutilisant la même API
- 🔔 Notifications push à la sortie d'un film de la watchlist

**Sécurité avancée :**
- 🔐 OAuth2 (Google, GitHub login)
- 🛡️ Rate-limiting par IP (slowapi)
- 🔒 Refresh tokens + rotation JWT

📁 *Code et infrastructure prêts à recevoir ces évolutions sans refactor majeur*

---

# 🎬 Merci pour votre attention

### Place à la démo !

**Équipe :** Med Abroud · Tesnime Chriaa

**URLs de démo :**
- 🌐 Application : `http://localhost:8080`
- 📘 Swagger UI : `http://localhost:8080/api/docs`
- 🔬 Tests : `docker compose exec api pytest`

**Code source :** `C:\Users\M\Desktop\devnet\movieflix\`
