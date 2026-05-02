# 01 — Backend : FastAPI + PostgreSQL

**Plan :** [2026-05-01-backend-foundation.md](../superpowers/plans/2026-05-01-backend-foundation.md)  
**Statut :** ✅ Terminé — 38 tests passent

---

## Contexte

Le backend expose une API REST que le frontend Tauri consomme via HTTP. Il gère la persistance de toutes les données (notes, dossiers, tâches, paramètres) et servira de fondation pour l'intégration de Bob (plan 6) et d'une authentification multi-utilisateurs future.

Il est déployé via Docker Compose aux côtés de PostgreSQL. Le frontend n'a jamais accès direct à la base de données — tout passe par l'API.

---

## Architecture

```
Frontend Tauri
      │  HTTP REST
      ▼
┌─────────────────────────────────┐
│  FastAPI app (main.py)          │
│                                 │
│  Routes (app/api/)              │  ← valide les entrées via Pydantic
│      │                          │
│  Services (app/services/)       │  ← logique métier, CRUD pur
│      │                          │
│  Models (app/models/)           │  ← SQLAlchemy ORM
│      │                          │
│  PostgreSQL                     │
└─────────────────────────────────┘
```

**Principe clé :** les routes ne contiennent aucune logique métier — elles valident l'entrée, appellent le service, et retournent la réponse. Toute la logique vit dans les services.

---

## Structure des fichiers

```
backend/
├── app/
│   ├── main.py                  # App FastAPI, CORS, routers, lifespan
│   ├── core/
│   │   ├── config.py            # Settings via pydantic-settings (.env)
│   │   └── database.py          # Engine SQLAlchemy, SessionLocal, get_db
│   ├── models/
│   │   ├── __init__.py          # Importe tous les modèles (requis pour create_all)
│   │   ├── folder.py            # Table folders (self-référentielle)
│   │   ├── note.py              # Table notes
│   │   ├── task.py              # Table tasks
│   │   └── setting.py           # Table settings (clé/valeur)
│   ├── schemas/
│   │   ├── folder.py            # FolderCreate, FolderUpdate, FolderRead
│   │   ├── note.py              # NoteCreate, NoteUpdate, NoteRead
│   │   ├── task.py              # TaskCreate, TaskUpdate, TaskRead
│   │   └── setting.py           # SettingRead, SettingWrite
│   ├── services/
│   │   ├── folders.py           # CRUD dossiers
│   │   ├── notes.py             # CRUD notes + favoris + récents
│   │   ├── tasks.py             # CRUD tâches + focus
│   │   └── settings.py          # Upsert clé/valeur
│   └── api/
│       ├── folders.py           # Router /api/folders
│       ├── notes.py             # Router /api/notes
│       ├── tasks.py             # Router /api/tasks
│       └── settings.py          # Router /api/settings
├── tests/
│   ├── conftest.py              # Fixtures pytest : SQLite in-memory + TestClient
│   ├── unit/                    # Tests services (pas d'HTTP, pas de Docker)
│   │   ├── test_notes.py
│   │   ├── test_tasks.py
│   │   ├── test_settings.py
│   │   └── test_folders.py
│   └── integration/
│       └── test_api.py          # Tests endpoints via TestClient
├── create_tables.py             # Crée les tables au démarrage Docker
├── Dockerfile
├── requirements.txt
└── .env.example                 # Variables d'environnement attendues
```

---

## Composants principaux

### `app/core/config.py`
Lit les variables d'environnement via `pydantic-settings`. Variable principale : `DATABASE_URL`. Le fichier `.env` est lu automatiquement si présent dans `backend/`.

### `app/core/database.py`
Crée l'engine SQLAlchemy et `SessionLocal`. Expose `get_db`, la dépendance FastAPI injectée dans chaque route pour obtenir une session DB propre par requête (ouverte et fermée automatiquement).

### `app/models/__init__.py`
Importe tous les modèles SQLAlchemy. Cet import est **obligatoire** : sans lui, `Base.metadata.create_all()` ne connaît pas les tables et ne les crée pas.

### `app/main.py`
Point d'entrée. Configure CORS (toutes origines en dev), monte les 4 routers. Le `lifespan` est vide pour l'instant — réservé aux hooks de démarrage futurs (ex: pool de connexions IA). La création des tables est déléguée à `create_tables.py` via le CMD Docker.

### Services (`app/services/`)
Chaque service expose des fonctions pures `(db: Session, ...) -> Model`. Aucun code HTTP ici. Les filtres SQLAlchemy utilisent `.is_(True)` / `.is_(False)` pour une génération SQL correcte.

---

## Lancer en local

### Avec Docker (recommandé)

```bash
# Depuis la racine du projet
docker compose up -d

# API disponible sur :
# http://localhost:8000
# http://localhost:8000/docs  (Swagger UI)
```

### Sans Docker (dev rapide)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Créer un fichier .env avec la DATABASE_URL d'une PostgreSQL locale
cp .env.example .env

# Créer les tables, puis lancer
python create_tables.py
uvicorn app.main:app --reload
```

---

## Tests

**38 tests — 0 échec.** Aucun Docker requis (SQLite in-memory via `StaticPool`).

```bash
cd backend
source .venv/bin/activate
python -m pytest tests/ -v
```

| Suite | Fichier | Tests |
|-------|---------|-------|
| Unit — Notes | `tests/unit/test_notes.py` | 9 |
| Unit — Tasks | `tests/unit/test_tasks.py` | 8 |
| Unit — Settings | `tests/unit/test_settings.py` | 7 |
| Unit — Folders | `tests/unit/test_folders.py` | 6 |
| Intégration | `tests/integration/test_api.py` | 8 |

**Architecture de test :** les tests unitaires testent les services directement (session SQLite). Les tests d'intégration utilisent `TestClient` + override de `get_db` pour simuler des requêtes HTTP sans démarrer de serveur.

---

## Liens

- [→ Référence API complète](./api-reference.md)
- [→ Schéma de base de données](./database-schema.md)
- [→ Plan d'implémentation](../superpowers/plans/2026-05-01-backend-foundation.md)
- [→ Spécifications générales](../specs/2026-05-01-app-design.md)
