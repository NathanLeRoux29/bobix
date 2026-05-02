# Référence API

Base URL : `http://localhost:8000`  
Documentation interactive : `http://localhost:8000/docs`

Toutes les réponses sont en JSON. Les erreurs retournent `{ "detail": "message" }`.

---

## Plan 1 — Backend

### Notes — `/api/notes`

| Méthode | Endpoint | Description | Code |
|---------|----------|-------------|------|
| GET | `/api/notes/` | Liste toutes les notes | 200 |
| GET | `/api/notes/recent?limit=4` | Notes les plus récentes | 200 |
| GET | `/api/notes/favorites` | Notes favorites | 200 |
| GET | `/api/notes/{id}` | Une note par ID | 200 / 404 |
| POST | `/api/notes/` | Créer une note | 201 |
| PATCH | `/api/notes/{id}` | Mise à jour partielle | 200 / 404 |
| DELETE | `/api/notes/{id}` | Supprimer | 204 / 404 |

**Paramètres GET `/api/notes/` :**
- `skip` (int, défaut 0) — pagination offset
- `limit` (int, défaut 100) — pagination limit

**Corps POST :**
```json
{
  "title": "Ma note",
  "content": "Contenu en Markdown",
  "folder_id": 1,
  "is_favorite": false
}
```

**Corps PATCH** (tous les champs optionnels) :
```json
{
  "title": "Nouveau titre",
  "content": "...",
  "folder_id": null,
  "is_favorite": true
}
```

**Réponse :**
```json
{
  "id": 1,
  "title": "Ma note",
  "content": "Contenu en Markdown",
  "folder_id": null,
  "is_favorite": false,
  "created_at": "2026-05-02T13:00:00Z",
  "updated_at": "2026-05-02T13:00:00Z"
}
```

---

### Dossiers — `/api/folders`

| Méthode | Endpoint | Description | Code |
|---------|----------|-------------|------|
| GET | `/api/folders/` | Liste tous les dossiers | 200 |
| GET | `/api/folders/{id}` | Un dossier par ID | 200 / 404 |
| POST | `/api/folders/` | Créer un dossier | 201 |
| PATCH | `/api/folders/{id}` | Renommer / déplacer | 200 / 404 |
| DELETE | `/api/folders/{id}` | Supprimer | 204 / 404 |

**Corps POST :**
```json
{
  "name": "Work",
  "parent_id": null
}
```

**Réponse :**
```json
{
  "id": 1,
  "name": "Work",
  "parent_id": null,
  "created_at": "2026-05-02T13:00:00Z"
}
```

> **Note :** Supprimer un dossier ne supprime pas ses notes — `folder_id` des notes enfants passe à `null`.

---

### Tâches — `/api/tasks`

| Méthode | Endpoint | Description | Code |
|---------|----------|-------------|------|
| GET | `/api/tasks/` | Liste toutes les tâches | 200 |
| GET | `/api/tasks/focus` | Tâches focus non terminées | 200 |
| GET | `/api/tasks/{id}` | Une tâche par ID | 200 / 404 |
| POST | `/api/tasks/` | Créer une tâche | 201 |
| PATCH | `/api/tasks/{id}` | Mise à jour partielle | 200 / 404 |
| DELETE | `/api/tasks/{id}` | Supprimer | 204 / 404 |

**Paramètres GET `/api/tasks/` :**
- `skip` (int, défaut 0)
- `limit` (int, défaut 100)

**Corps POST :**
```json
{
  "title": "Préparer la présentation",
  "description": "Slides pour le lundi",
  "due_date": "2026-05-10",
  "tag": "work",
  "is_focus": true,
  "is_completed": false
}
```

**Réponse :**
```json
{
  "id": 1,
  "title": "Préparer la présentation",
  "description": "Slides pour le lundi",
  "due_date": "2026-05-10",
  "tag": "work",
  "is_focus": true,
  "is_completed": false,
  "created_at": "2026-05-02T13:00:00Z",
  "updated_at": "2026-05-02T13:00:00Z"
}
```

---

### Paramètres — `/api/settings`

Stockage clé/valeur pour les préférences utilisateur (thèmes, config Bob, etc.).

| Méthode | Endpoint | Description | Code |
|---------|----------|-------------|------|
| GET | `/api/settings/` | Toutes les clés/valeurs | 200 |
| PUT | `/api/settings/{key}` | Créer ou mettre à jour une clé | 200 |

**Corps PUT :**
```json
{ "value": "dark" }
```

**Réponse :**
```json
{ "key": "theme", "value": "dark" }
```

**Exemples de clés utilisées par l'app :**

| Clé | Description |
|-----|-------------|
| `theme` | Thème actif |
| `username` | Nom affiché dans la salutation |
| `greeting_template` | Template de salutation |
| `bob_provider` | Provider IA (anthropic / openai / ollama) |
| `bob_model` | Modèle IA sélectionné |
