# Schéma de base de données

**SGBD :** PostgreSQL 15  
**ORM :** SQLAlchemy 2.0  
**Fichiers modèles :** `backend/app/models/`

Les tables sont créées automatiquement via `create_tables.py` au démarrage Docker. Pas d'Alembic pour l'instant — à intégrer avant une mise en production.

---

## Plan 1 — Backend

### `folders`

```sql
CREATE TABLE folders (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    parent_id  INTEGER REFERENCES folders(id),
    created_at TIMESTAMPTZ DEFAULT now()
);
```

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Clé primaire |
| `name` | VARCHAR(255) | Nom du dossier |
| `parent_id` | INTEGER | Dossier parent (null = racine) |
| `created_at` | TIMESTAMPTZ | Date de création |

**Relation :** auto-référentielle via `parent_id` — permet l'imbrication illimitée de dossiers.

---

### `notes`

```sql
CREATE TABLE notes (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(255) NOT NULL,
    content     TEXT NOT NULL DEFAULT '',
    folder_id   INTEGER REFERENCES folders(id),
    is_favorite BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);
```

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Clé primaire |
| `title` | VARCHAR(255) | Titre de la note |
| `content` | TEXT | Contenu Markdown |
| `folder_id` | INTEGER | Dossier parent (null = racine) |
| `is_favorite` | BOOLEAN | Affichée dans les favoris du Hub |
| `created_at` | TIMESTAMPTZ | Date de création |
| `updated_at` | TIMESTAMPTZ | Mise à jour à chaque PATCH |

> `updated_at` est mis à jour manuellement dans `services/notes.py` — SQLAlchemy `onupdate` ne se déclenche pas toujours en dehors des sessions flush.

---

### `tasks`

```sql
CREATE TABLE tasks (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    description  TEXT,
    due_date     DATE,
    tag          VARCHAR(100),
    is_focus     BOOLEAN NOT NULL DEFAULT false,
    is_completed BOOLEAN NOT NULL DEFAULT false,
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_at   TIMESTAMPTZ DEFAULT now()
);
```

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Clé primaire |
| `title` | VARCHAR(255) | Titre de la tâche |
| `description` | TEXT | Description détaillée |
| `due_date` | DATE | Date d'échéance |
| `tag` | VARCHAR(100) | Catégorie libre |
| `is_focus` | BOOLEAN | Affichée dans le widget Hub "Tasks Focus" |
| `is_completed` | BOOLEAN | Tâche terminée |
| `created_at` | TIMESTAMPTZ | Date de création |
| `updated_at` | TIMESTAMPTZ | Mise à jour à chaque PATCH |

---

### `settings`

```sql
CREATE TABLE settings (
    id    SERIAL PRIMARY KEY,
    key   VARCHAR(255) NOT NULL UNIQUE,
    value TEXT
);
CREATE INDEX ix_settings_key ON settings(key);
```

| Colonne | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Clé primaire |
| `key` | VARCHAR(255) | Clé unique (ex: `theme`, `username`) |
| `value` | TEXT | Valeur sérialisée en texte |

**Usage :** toutes les préférences utilisateur (thèmes, config Bob, salutation) sont stockées ici sous forme clé/valeur. L'endpoint `PUT /api/settings/{key}` est idempotent — crée ou met à jour.

---

## Évolutions prévues

| Plan | Tables ajoutées / modifiées |
|------|-----------------------------|
| Plan 6 — Bob | `conversations`, `messages` (historique optionnel) |
| Future — Auth | `users` + colonnes `user_id` sur toutes les tables |
