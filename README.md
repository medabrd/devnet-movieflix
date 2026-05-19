# 🎬 MovieFlix — Mini-projet DevNet

Application web complète consommant l'API **TMDB**, avec authentification, watchlist persistante, conteneurisation et déploiement automatisé.

## Stack

| Couche | Techno |
|---|---|
| Backend | **FastAPI** (Python 3.12), SQLAlchemy, JWT |
| Frontend | **React 18** + Vite, servi par **Nginx** |
| Base de données | **PostgreSQL 16** |
| API externe | **TMDB** (The Movie Database) |
| Conteneurisation | **Docker** + **Docker Compose** |
| Automatisation | **Ansible** + **Bash** |
| CI/CD | **GitHub Actions** (lint, tests, build) |

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Browser     │───▶│  Nginx (web) │───▶│  FastAPI     │
└──────────────┘    │  React SPA   │    │  (api)       │
                    └──────────────┘    └──────┬───────┘
                                               │
                                       ┌───────┴────────┐
                                       │                │
                                  ┌────▼────┐     ┌─────▼─────┐
                                  │ Postgres│     │ TMDB API  │
                                  │  (db)   │     │ (externe) │
                                  └─────────┘     └───────────┘
```

## Démarrage rapide

### 1. Pré-requis
- Docker + Docker Compose
- Une clé API TMDB gratuite : https://www.themoviedb.org/settings/api

### 2. Configuration
```bash
cp .env.example .env
# Éditer .env et mettre TMDB_API_KEY=...
```

### 3. Déploiement local (zéro intervention)
```bash
./scripts/deploy.sh local
# UI : http://localhost:8080
# API docs : http://localhost:8080/api/docs (proxy via Nginx)
```

### 4. Déploiement distant via Ansible
```bash
# 1) Éditer ansible/inventory.ini (mettre l'IP/host du serveur)
# 2) Lancer :
./scripts/deploy.sh remote
```

## Tests
```bash
cd backend
pip install -r requirements.txt
pytest
```

## Fonctionnalités

- 🔥 Tendances de la semaine (TMDB `/trending/movie/week`)
- 🔎 Recherche de films
- 🔐 Inscription / connexion (JWT)
- ⭐ Watchlist persistante par utilisateur
- 🩺 Endpoint `/api/health` + healthchecks Docker

## Sécurité

- Mots de passe hashés (bcrypt)
- JWT signé (HS256) avec secret en variable d'env
- Conteneurs en utilisateur non-root (backend)
- Headers de sécurité Nginx
- CORS restrictif côté backend
- Secrets jamais commités (`.env` ignoré)

## CI/CD

À chaque push sur `main` :
1. **Lint** (ruff) du backend
2. **Tests** pytest avec base SQLite éphémère
3. **Build** frontend (Vite)
4. **Build** images Docker (backend + frontend)
