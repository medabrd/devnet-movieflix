# 🎓 Guide débutant — Comprendre et lancer MovieFlix

Ce guide te permet de comprendre **chaque brique** du projet et de lancer la démo manuellement, **étape par étape**, sans aucun script automatique.

---

## PARTIE 1 — Comprendre les concepts en 10 minutes

### 1.1 C'est quoi une application web "moderne" ?

Une application web moderne est découpée en **3 morceaux séparés** qui communiquent :

```
┌─────────────┐  HTTP   ┌─────────────┐  SQL   ┌─────────────┐
│  FRONTEND   │ ──────▶ │   BACKEND   │ ─────▶ │ BASE DONNÉES│
│  (React)    │ ◀────── │  (FastAPI)  │ ◀───── │ (PostgreSQL)│
│  ce que     │  JSON   │   logique   │        │  stockage   │
│  l'user voit│         │   métier    │        │  permanent  │
└─────────────┘         └─────────────┘        └─────────────┘
                              │
                              │ HTTP
                              ▼
                        ┌─────────────┐
                        │  API TMDB   │
                        │  (externe)  │
                        └─────────────┘
```

- **Frontend** : ce que l'utilisateur voit dans son navigateur (HTML, CSS, JS = React).
- **Backend** : un programme serveur en Python qui reçoit les requêtes du frontend et répond.
- **Base de données** : où on stocke durablement les comptes utilisateurs et les watchlists.
- **API externe (TMDB)** : un service tiers gratuit qui nous fournit les données des films.

### 1.2 Qu'est-ce que Docker ?

**Problème classique** : "ça marche chez moi mais pas chez toi" → versions différentes de Python, de Node, OS différents, etc.

**Solution Docker** : on emballe chaque morceau (frontend, backend, BDD) dans une **"boîte" isolée** (un *conteneur*) qui contient TOUT ce qu'il faut pour fonctionner. La boîte tourne pareil sur n'importe quelle machine.

- **Image Docker** = recette de la boîte (fichier `Dockerfile`).
- **Conteneur** = la boîte en train de tourner.
- **Docker Compose** = un chef d'orchestre qui lance plusieurs boîtes ensemble (fichier `docker-compose.yml`).

### 1.3 Pourquoi FastAPI ?

C'est un framework Python qui transforme tes fonctions Python en **API REST** automatiquement. Tu écris :

```python
@app.get("/api/movies/trending")
async def trending():
    return {...}
```

Et tu obtiens une URL qui répond à `GET http://...:8000/api/movies/trending`. Bonus : **Swagger UI** te génère une interface pour tester l'API sans écrire de code.

### 1.4 Pourquoi Ansible ?

C'est un outil d'**automatisation**. Au lieu de te connecter en SSH sur un serveur et taper 50 commandes pour installer Docker, copier les fichiers, lancer l'app… tu écris **une fois** un fichier YAML (`deploy.yml`) qui décrit l'état désiré, et Ansible fait tout. **Idempotent** = tu peux le relancer 100 fois, ça ne casse rien.

### 1.5 C'est quoi un pipeline CI/CD ?

Quand tu pushes ton code sur GitHub, **GitHub Actions** lance automatiquement :
1. Les tests
2. La vérification de la qualité du code (lint)
3. La construction des images Docker

Si quelque chose casse, tu es notifié. → Tu ne déploies jamais du code cassé.

---

## PARTIE 2 — Installer les pré-requis

### 2.1 Installer Docker Desktop (obligatoire)

1. Va sur https://www.docker.com/products/docker-desktop/
2. Télécharge **Docker Desktop for Windows** et installe-le.
3. **Redémarre** ton PC si demandé.
4. Lance **Docker Desktop** (icône baleine 🐳). Attends qu'il affiche "Engine running".

Vérifie dans PowerShell :
```powershell
docker --version
docker compose version
```
Tu dois voir une version pour les deux. Si erreur, Docker Desktop n'est pas démarré.

### 2.2 Récupérer une clé API TMDB (gratuit, 2 minutes)

1. Crée un compte sur https://www.themoviedb.org/signup
2. Une fois connecté, va dans **Settings → API** (https://www.themoviedb.org/settings/api).
3. Clique "Create" → "Developer" → remplis le formulaire (mets ce que tu veux, ex: usage = "Educational").
4. Récupère ta **"API Key (v3 auth)"** — c'est une chaîne du type `8a1b2c3d4e5f6...`.

⚠️ **Garde cette clé**, on va l'utiliser à l'étape suivante.

---

## PARTIE 3 — Lancer le projet ÉTAPE PAR ÉTAPE (manuel)

Ouvre **PowerShell**. Tous les chemins sont absolus pour éviter toute confusion.

### 3.1 Configurer le fichier `.env`

Le fichier `.env` contient les **secrets** (clé API, mot de passe BDD, etc.). Il ne doit JAMAIS être commité sur GitHub.

```powershell
cd C:\Users\M\Desktop\devnet\movieflix
Copy-Item .env.example .env
```

Ouvre maintenant `.env` avec le bloc-notes :
```powershell
notepad .env
```

Et remplace `your_tmdb_api_key_here` par **ta vraie clé TMDB**. Sauvegarde et ferme.

Ton `.env` doit ressembler à :
```
TMDB_API_KEY=8a1b2c3d4e5f67890abcdef1234567
POSTGRES_USER=movieflix
POSTGRES_PASSWORD=movieflix
POSTGRES_DB=movieflix
JWT_SECRET=un-secret-tres-long-et-aleatoire
WEB_PORT=8080
```

### 3.2 Lancer la stack avec Docker Compose

**Une seule commande** lance les 3 conteneurs (BDD, API, web) :

```powershell
docker compose up --build
```

**Ce qui se passe** (tu vas voir tout ça défiler dans ta console) :

1. Docker télécharge l'image **PostgreSQL 16** depuis Docker Hub (la 1re fois seulement).
2. Docker construit l'image **backend** : il installe Python 3.12, puis les dépendances de `requirements.txt`.
3. Docker construit l'image **frontend** : `npm install`, puis `npm run build`, puis copie dans Nginx.
4. Docker démarre les 3 conteneurs et les met sur le **même réseau** (`movieflix`).
5. Le backend attend que la BDD soit prête (`condition: service_healthy`), puis se lance.
6. Le frontend Nginx démarre et proxy les requêtes `/api/*` vers le backend.

⏳ La **1re fois**, ça prend 3-5 minutes (téléchargements). Ensuite c'est ~10 secondes.

➡️ Quand tu vois `movieflix-api  | INFO: Uvicorn running on http://0.0.0.0:8000`, c'est prêt.

### 3.3 Tester la démo

**Ouvre dans ton navigateur** :

| URL | Ce que tu vois |
|---|---|
| http://localhost:8080 | L'application MovieFlix (tendances) |
| http://localhost:8080/api/docs | **Swagger UI** — interface auto de l'API |
| http://localhost:8080/api/health | `{"status":"ok"}` |

**Scénario de démo** :
1. Sur http://localhost:8080 → tu vois les films tendances (← appel à TMDB en live).
2. Tape "matrix" dans la barre de recherche → résultats de recherche.
3. Clique "Connexion" en haut → "Pas de compte ? S'inscrire".
4. Crée un compte (`alice` / `password123`).
5. Tu es redirigé sur l'accueil. Clique "+ Watchlist" sur n'importe quel film.
6. Va dans "Ma liste" → tu vois le film. Clique "Retirer" → il disparaît.
7. **Rafraîchis la page** → la watchlist est toujours là (← donnée persistée en PostgreSQL).

### 3.4 Voir ce qui tourne (commandes utiles)

Dans un **autre** PowerShell (laisse le 1er tourner) :

```powershell
# Lister les conteneurs
docker ps

# Voir les logs en direct du backend
docker logs -f movieflix-api

# Entrer dans le conteneur backend (pour debug)
docker exec -it movieflix-api /bin/bash

# Entrer dans la BDD PostgreSQL
docker exec -it movieflix-db psql -U movieflix -d movieflix
# Une fois dedans :  SELECT * FROM users;  → voir les comptes
#                    \q   pour quitter
```

### 3.5 Arrêter / nettoyer

```powershell
# Arrêter (Ctrl+C dans la console qui tourne, ou) :
docker compose down

# Tout supprimer (y compris les données BDD) :
docker compose down -v
```

---

## PARTIE 4 — Lancer les tests automatisés

Le projet contient des **tests pytest** (validation auto de la logique). Tu peux les lancer **sans rien installer en Python** grâce à Docker :

```powershell
docker compose exec api pytest
```

Tu dois voir quelque chose comme :
```
tests/test_auth_watchlist.py ...                                 [ 60%]
tests/test_health.py .                                            [ 80%]
tests/test_movies.py .                                            [100%]
======== 5 passed in 1.23s ========
```

✅ Tous les tests passent = la logique est validée automatiquement.

---

## PARTIE 5 — Comprendre la structure des fichiers

```
movieflix/
├── backend/                 ← le serveur Python
│   ├── app/
│   │   ├── main.py          ← point d'entrée FastAPI
│   │   ├── config.py        ← variables d'environnement
│   │   ├── database.py      ← connexion PostgreSQL
│   │   ├── models.py        ← tables SQL (User, WatchlistItem)
│   │   ├── schemas.py       ← formats JSON (Pydantic)
│   │   ├── security.py      ← JWT + bcrypt
│   │   ├── routers/         ← les URLs de l'API
│   │   │   ├── auth.py      ← /api/auth/register, /api/auth/login
│   │   │   ├── movies.py    ← /api/movies/*  (parle à TMDB)
│   │   │   └── watchlist.py ← /api/watchlist/*  (BDD)
│   │   └── services/
│   │       └── tmdb.py      ← client HTTP qui appelle TMDB
│   ├── tests/               ← tests pytest
│   ├── Dockerfile           ← recette image backend
│   └── requirements.txt     ← dépendances Python
│
├── frontend/                ← l'interface React
│   ├── src/
│   │   ├── main.jsx         ← point d'entrée React
│   │   ├── App.jsx          ← navigation
│   │   ├── api.js           ← appels HTTP vers le backend
│   │   ├── pages/           ← Home, Watchlist, Login
│   │   └── components/      ← MovieCard
│   ├── Dockerfile           ← multi-stage : build + Nginx
│   ├── nginx.conf           ← config serveur web + proxy /api
│   └── package.json         ← dépendances JS
│
├── ansible/
│   ├── deploy.yml           ← playbook qui déploie sur un serveur
│   └── inventory.ini        ← liste des serveurs cibles
│
├── scripts/
│   └── deploy.sh            ← raccourci bash : 1 commande = tout
│
├── .github/workflows/
│   └── ci-cd.yml            ← pipeline GitHub Actions (CI/CD)
│
├── docker-compose.yml       ← orchestration des 3 conteneurs
├── .env.example             ← modèle de fichier de secrets
├── .env                     ← tes vrais secrets (NON commités)
└── README.md
```

---

## PARTIE 6 — Le déroulé type pour la soutenance (5 min)

| Temps | Ce que tu fais | Ce que tu dis |
|---|---|---|
| 0:00 | Montre l'archi sur slide 2 | "Notre app a 3 conteneurs orchestrés par Docker Compose" |
| 0:30 | `docker compose up -d` dans un terminal | "Une seule commande lance toute la stack" |
| 1:00 | `docker ps` | "Voici les 3 conteneurs : web, api, db, tous healthy" |
| 1:30 | Ouvre http://localhost:8080 | "Voici les films tendances, récupérés en live depuis TMDB" |
| 2:00 | Tape une recherche "inception" | "L'API REST de TMDB est consommée par notre backend" |
| 2:30 | Ouvre http://localhost:8080/api/docs | "Swagger nous documente automatiquement nos endpoints" |
| 3:00 | Inscris-toi + ajoute un film à la watchlist | "Authentification JWT + persistance PostgreSQL" |
| 3:30 | Rafraîchis → watchlist toujours là | "Les données sont bien persistées" |
| 4:00 | `docker compose exec api pytest` | "Les tests automatisés valident la logique" |
| 4:30 | Montre le workflow GitHub Actions | "Et tout ça est intégré dans un pipeline CI/CD" |

---

## PARTIE 7 — Que répondre aux questions du jury ?

### "Pourquoi FastAPI plutôt que Flask ou Django ?"
> FastAPI est asynchrone par défaut (important pour appeler une API externe comme TMDB), il valide automatiquement les données avec Pydantic, et génère la doc OpenAPI/Swagger gratuitement. Django est plus lourd, Flask demande plus de plomberie manuelle.

### "Comment fonctionne l'authentification ?"
> On utilise **JWT (JSON Web Token)**. Quand l'utilisateur se connecte, le backend signe un token avec un secret et le renvoie. Le frontend stocke ce token dans `localStorage` et l'envoie dans le header `Authorization: Bearer <token>` à chaque requête. Le backend vérifie la signature pour valider l'utilisateur — pas besoin de session côté serveur (stateless).

### "Pourquoi Docker Compose et pas juste Docker ?"
> Compose permet de définir **plusieurs services qui dépendent les uns des autres** dans un seul fichier YAML. On peut aussi définir un réseau privé, des volumes persistants, et l'ordre de démarrage (le backend attend que la BDD soit prête).

### "Pourquoi un build multi-stage pour le frontend ?"
> Le build (avec Node.js) produit des fichiers HTML/CSS/JS statiques. On n'a pas besoin de Node.js en production. Le multi-stage permet de **construire** dans une image Node, puis de **servir** dans une image Nginx beaucoup plus légère (~30 MB au lieu de ~1 GB).

### "Quelles sont les mesures de sécurité ?"
> 1. Mots de passe **hashés avec bcrypt** (jamais en clair). 2. **JWT signé** côté serveur. 3. Conteneur backend en **utilisateur non-root**. 4. **Headers de sécurité** Nginx (X-Frame-Options, X-Content-Type-Options). 5. **Secrets** en variables d'environnement, jamais dans le code. 6. **CORS** restrictif côté backend.

### "Comment déployer en production ?"
> Deux options : 1. En **local/VM**, le script `deploy.sh local` qui lance `docker compose up`. 2. Sur un **serveur distant**, le playbook **Ansible** qui se connecte en SSH, installe Docker, copie le code et démarre la stack. Le déploiement est **idempotent** : on peut le rejouer sans risque.

### "Et si TMDB est down ?"
> Le client TMDB gère les erreurs HTTP : si l'API est inaccessible, le backend renvoie un **502 Bad Gateway** avec un message explicite. On pourrait améliorer avec un cache Redis pour servir les dernières réponses connues.

---

## PARTIE 8 — Dépannage rapide

| Problème | Cause probable | Solution |
|---|---|---|
| `docker: command not found` | Docker Desktop pas installé/démarré | Lancer Docker Desktop |
| `port 8080 already in use` | Un autre service utilise 8080 | Changer `WEB_PORT=9090` dans `.env` |
| Page blanche sur http://localhost:8080 | Frontend pas encore construit | Attendre, regarder les logs |
| `TMDB authentication failed` | Clé API mauvaise/manquante | Vérifier `TMDB_API_KEY` dans `.env` |
| Watchlist vide après reconnexion | Conteneur DB recréé | Ne pas faire `docker compose down -v` |
| Slow build à chaque fois | Pas de cache | Garder Docker Desktop allumé |

---

## 🎬 Tu es prêt !

Récap : tu lances avec **`docker compose up --build`**, tu démos sur **http://localhost:8080**, et tu réponds aux questions avec les réponses préparées de la Partie 7.

Bonne soutenance ! 🚀
