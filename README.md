# Bobix

Application desktop de gestion de notes et tâches avec un assistant IA intégré (Bob).

**Stack :** Tauri 2.x + Vue 3 + TypeScript · FastAPI + PostgreSQL · Claude / OpenAI / Ollama

---

## Prérequis

| Outil | Version | Usage |
|-------|---------|-------|
| Node.js | 20+ | Frontend |
| Rust | stable | Tauri (desktop) |
| Docker + Docker Compose | — | Backend + PostgreSQL |

**Dépendances système Tauri (Linux) :**

```bash
# Ubuntu / Debian
sudo apt install libwebkit2gtk-4.1-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

> Documentation complète : https://tauri.app/start/prerequisites/

---

## Structure du projet

```
app/
├── frontend/          # Tauri + Vue 3 (application desktop)
│   ├── src/           # Code Vue / TypeScript
│   ├── src-tauri/     # Code Rust / config Tauri
│   └── package.json
├── backend/           # FastAPI + SQLAlchemy
│   └── app/
├── docs/              # Documentation technique
│   ├── dev/           # Guides développeur
│   └── superpowers/   # Plans d'implémentation
└── docker-compose.yml # PostgreSQL + Backend
```

---

## Lancer l'application

### 1. Démarrer le backend (Docker)

```bash
# Depuis la racine du projet
docker compose up -d
```

Démarre PostgreSQL (port 5442) et l'API FastAPI (port 8000).

Vérifier que l'API répond :
```bash
curl http://localhost:8000/health
```

### 2. Lancer le frontend

```bash
cd frontend
npm install      # première fois seulement
```

**Mode navigateur** (développement rapide, pas de Tauri) :
```bash
npm run dev
# → http://localhost:1420
```

**Mode desktop Tauri** (application native) :
```bash
npm run tauri dev
```

> La première compilation Rust prend 2-3 minutes. Les suivantes sont très rapides.

**Build production Tauri** :
```bash
npm run build
# ou
npm run tauri build
```

---

## Prérequis Tauri — Rust

Rust est requis uniquement pour `npm run tauri dev` et `npm run tauri build`. Pour le développement quotidien, `npm run dev` suffit.

```bash
# Installer Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Recharger le shell
source ~/.cargo/env

# Vérifier
cargo --version
```

---

## Dépannage

### `failed to run 'cargo metadata'`

Rust n'est pas installé ou pas dans le PATH. Voir la section **Prérequis Tauri** ci-dessus.

### `Port 1420 is already in use`

Un serveur Vite tourne déjà en arrière-plan. Le tuer puis relancer :

```bash
kill $(lsof -t -i:1420)
npm run tauri dev
```

### Tout en une commande (script de démarrage)

```bash
./start.sh
```

Lance Docker Compose + le serveur Vite en parallèle.

---

## Tests

```bash
cd frontend
npm test
```

16 tests, aucun backend requis (fonctions pures + mock fetch).

---

## Flux de navigation

```
Démarrage → /greeting (splash 3.2s) → /hub (avec sidebar)
                                            ↓
                              /notes · /tasks · /settings
```

La page de salutation est un écran de chargement plein écran. Elle affiche un message personnalisé avec animation, puis redirige automatiquement vers le hub. Si le backend est indisponible, les valeurs par défaut sont utilisées.

---

## Plans d'implémentation

| # | Plan | Statut |
|---|------|--------|
| 1 | [Backend FastAPI CRUD](docs/superpowers/plans/2026-05-01-backend.md) | ✅ Terminé |
| 2 | [Frontend base Tauri/Vue](docs/superpowers/plans/2026-05-01-frontend-base.md) | ✅ Terminé |
| 3 | [Hub — Dashboard widgets](docs/superpowers/plans/2026-05-01-hub.md) | ⏳ À venir |
| 4 | [Notes — Éditeur Markdown](docs/superpowers/plans/2026-05-01-notes.md) | ⏳ À venir |
| 5 | [Tâches — Liste + filtres](docs/superpowers/plans/2026-05-01-tasks.md) | ⏳ À venir |
| 6 | [Bob — Intégration LLM](docs/superpowers/plans/2026-05-01-bob.md) | ⏳ À venir |
| 7 | [Paramètres](docs/superpowers/plans/2026-05-01-settings.md) | ⏳ À venir |

---

## Documentation développeur

- [01 — Backend](docs/dev/01-backend.md)
- [02 — Frontend](docs/dev/02-frontend.md)
- [Référence API](docs/dev/api-reference.md)
- [Schéma base de données](docs/dev/database-schema.md)
