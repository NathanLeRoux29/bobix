# 02 — Frontend : Tauri + Vue 3

**Plan :** [2026-05-01-frontend-base.md](../superpowers/plans/2026-05-01-frontend-base.md)
**Statut :** ✅ Terminé — 23 tests passent

---

## Contexte

Le frontend est une application desktop Tauri 2.x intégrant Vue 3 + TypeScript. Il consomme l'API FastAPI via `fetch` HTTP standard. Le frontend ne se connecte jamais directement à la base de données — tout passe par `http://localhost:8000`.

---

## Architecture

```
Tauri WebView (frontend/)
      │  fetch HTTP
      ▼
┌────────────────────────────────────┐
│  Vue Router (src/router/)          │  ← navigation entre écrans
│                                    │
│  Views (src/views/)                │  ← un fichier par écran
│      │                             │
│  Pinia Stores (src/stores/)        │  ← état global + appels API
│      │                             │
│  Utils (src/utils/)                │  ← fonctions pures testables
│                                    │
│  CSS Variables (assets/styles/)    │  ← thème centralisé
└────────────────────────────────────┘
```

---

## Structure des fichiers

```
frontend/
├── package.json
├── vite.config.ts               # Config Vite + Vitest
├── tsconfig.json
├── index.html
│
├── src/
│   ├── main.ts                  # Point d'entrée Vue
│   ├── App.vue                  # Shell : <RouterView />
│   │
│   ├── assets/
│   │   └── styles/
│   │       └── default.css      # Variables CSS (thème sombre)
│   │
│   ├── router/
│   │   └── index.ts             # Routes: /greeting + nested layout
│   │
│   ├── layouts/
│   │   └── AppLayout.vue        # Sidebar + <RouterView>
│   │
│   ├── stores/
│   │   ├── settings.ts          # Pinia: préférences utilisateur
│   │   └── notes.ts             # Pinia: notes, dossiers, onglets, auto-save
│   │
│   ├── types/
│   │   └── notes.ts             # Interfaces Note et Folder
│   │
│   ├── utils/
│   │   └── greeting.ts          # getTimeOfDay, getGreetingMessage
│   │
│   ├── components/
│   │   └── notes/
│   │       ├── NotesActionBar.vue   # Barre latérale gauche
│   │       ├── NotesTabs.vue        # Barre d'onglets avec statut sauvegarde
│   │       ├── NotesEditor.vue      # Éditeur WYSIWYG TipTap + barre markdown
│   │       ├── FilesModal.vue       # Explorateur de fichiers complet
│   │       └── BobPanel.vue         # Panel IA Bob (placeholder)
│   │
│   ├── views/
│   │   ├── GreetingView.vue     # Splash screen de démarrage
│   │   ├── HubView.vue          # Dashboard (placeholder)
│   │   ├── NotesView.vue        # Module Notes complet
│   │   ├── TasksView.vue        # Tâches (placeholder)
│   │   └── SettingsView.vue     # Paramètres (placeholder)
│   │
│   └── __tests__/
│       ├── greeting.test.ts
│       ├── settings.store.test.ts
│       └── notes.store.test.ts
│
└── src-tauri/                   # Rust / Tauri
```

---

## Module Notes

Le module Notes est le module principal de l'application. Il couvre la gestion complète de notes en markdown avec dossiers, onglets, explorateur de fichiers et éditeur WYSIWYG.

### `src/stores/notes.ts` — `useNotesStore`

Store Pinia central du module. Gère les onglets ouverts, l'auto-save, et toutes les opérations CRUD sur notes et dossiers.

**État :**

| Propriété | Type | Rôle |
|-----------|------|------|
| `openTabs` | `Note[]` | Notes ouvertes en onglets |
| `activeTabId` | `number \| null` | Onglet actif |
| `allNotes` | `Note[]` | Toutes les notes chargées |
| `folders` | `Folder[]` | Tous les dossiers |
| `pendingContent` | `string` | Contenu en cours d'édition (non sauvegardé) |
| `pendingTitle` | `string` | Titre en cours d'édition |
| `saveStatus` | `SaveStatus` | `idle \| saving \| saved \| error` |
| `isBobVisible` | `boolean` | Visibilité du panel Bob |

**Actions principales :**

| Action | Description |
|--------|-------------|
| `fetchNotes()` | `GET /api/notes/` — charge `allNotes` |
| `fetchFolders()` | `GET /api/folders/` — charge `folders` |
| `openNote(id)` | Ouvre une note dans un onglet (fetch si absente) |
| `closeTab(id)` | Ferme un onglet, sauvegarde si pendingContent |
| `scheduleSave()` | Debounce 1s puis `saveNote()` |
| `saveNote()` | `PATCH /api/notes/{id}` avec titre + contenu |
| `createNote(folderId?)` | `POST /api/notes/` puis ouvre dans un onglet |
| `renameNote(id, title)` | `PATCH /api/notes/{id}` — mise à jour optimiste |
| `deleteNote(id)` | `DELETE /api/notes/{id}` |
| `toggleFavorite(id)` | `PATCH /api/notes/{id}` — met à jour `openTabs` ET `allNotes` |
| `copyNote(sourceId, folderId, title)` | `POST /api/notes/` en dupliquant le contenu |
| `createFolder(name, parentId?)` | `POST /api/folders/` |
| `renameFolder(id, name)` | `PATCH /api/folders/{id}` — mise à jour optimiste |
| `deleteFolder(id)` | `DELETE /api/folders/{id}` |
| `moveNote(noteId, folderId)` | `PATCH /api/notes/{id}` — mise à jour optimiste avec rollback |
| `moveFolder(folderId, parentId)` | `PATCH /api/folders/{id}` — mise à jour optimiste avec rollback |

> **Piège :** `openTabs` et `allNotes` sont des tableaux séparés avec des objets distincts. `toggleFavorite` doit mettre à jour les deux références. Le store utilise `??` pour trouver la note mais applique la mutation sur les deux.

**Auto-save :**
Un timer externe (`saveTimer`) déclenche `saveNote()` 1 seconde après la dernière frappe. En cas d'erreur réseau, une retry automatique se fait après 3 secondes.

---

### `src/components/notes/NotesEditor.vue`

Éditeur WYSIWYG basé sur **TipTap 3** + **tiptap-markdown**. Le contenu est toujours stocké et sauvegardé en markdown.

**Extensions TipTap utilisées :**

| Extension | Rôle |
|-----------|------|
| `StarterKit` | Headings, bold, italic, strike, code, listes, blockquote, HR, undo/redo natif |
| `TextStyle` | Support de styles inline (requis par Color) |
| `Color` | Couleur de texte (`setColor` / `unsetColor`) |
| `Highlight` (multicolor) | Surlignage avec couleur (`setHighlight` / `unsetHighlight`) |
| `tiptap-markdown` | Import/export markdown — `editor.storage.markdown.getMarkdown()` |

**Barre d'outils :**
- Layout 3 colonnes CSS grid : titre (gauche) — boutons formatage (centre) — actions (droite)
- Boutons : H1/H2/H3, Gras, Italique, Barré, Code inline, Bloc de code, Citation, Liste, Liste numérotée, Séparateur
- Palette couleurs : 9 couleurs pour le texte + 9 couleurs pastel pour le surlignage
- Les boutons s'allument (`isActive`) selon le contexte du curseur

**Undo/Redo :** géré nativement par TipTap (History inclus dans StarterKit). Ctrl+Z / Ctrl+Y / Ctrl+Shift+Z.

**Synchronisation avec le store :**
- `onUpdate` → `editor.storage.markdown.getMarkdown()` → `store.pendingContent`
- Changement d'onglet (`watch activeTabId`) → `editor.commands.setContent(store.pendingContent)`

---

### `src/components/notes/FilesModal.vue`

Explorateur de fichiers modal complet. Remplace une ancienne liste plate.

**Navigation :**
- `currentFolderId: number | null` — dossier affiché (null = racine)
- `navStack: NavEntry[]` — pile pour le breadcrumb (cliquable pour remonter)
- Cliquer un dossier → `enterFolder()` — cliquer une note → `openNote()` + ferme la modal

**Modes d'affichage :**
- Liste ou grille, persisté dans `localStorage("notes-view-mode")`

**Recherche :**
- Filtre global sur toutes les notes et dossiers (pas limité au dossier courant)
- Le breadcrumb est masqué pendant la recherche

**Sélection multiple :**
- `selectedItems: Set<string>` — clés de la forme `"note:5"` ou `"folder:3"`
- Ctrl+clic : toggle sélection individuelle
- Shift+clic : sélection en plage (basé sur `lastSelectedIndex`)
- Long press 300ms (mobile/tactile) : active la sélection

**Drag & Drop (HTML5 natif) :**
- Déposer une note/dossier sur un dossier → `moveNote` / `moveFolder`
- Déposer sur le breadcrumb → déplace vers ce niveau (bloqué sur le segment actif)
- Réordonner dans le dossier courant → `localItems` (ordre local non persisté)
- Protection cycle : `isDescendant()` empêche de déplacer un dossier dans l'un de ses enfants
- `localItems` : tableau ordonné local qui préserve l'ordre du drag. Synchronisé via `watch([currentFolderId, currentFolders, currentNotes], buildLocalItems)`

**Copier/Coller :**
- `clipboard: ClipboardItem[]` — notes uniquement
- Copie individuelle (menu contextuel) ou multi-sélection (Ctrl+C)
- Coller (Ctrl+V ou menu fond) → `copyNote()` dans le dossier courant
- `uniqueTitle()` auto-incrémente : `"Note"` → `"Note (1)"` → `"Note (2)"`

**Menu contextuel :**
- Téléporté dans `<body>` via `<Teleport>` pour éviter les conflits z-index
- 4 variantes : `note` | `folder` | `background` | `multiselect`
- En mode favoris : option "Enlever des favoris" (appelle `toggleFavorite` sans supprimer)

---

### `src/components/notes/NotesTabs.vue`

Barre d'onglets horizontale avec scroll horizontal discret (scrollbar fine).

- Affiche `store.openTabs` — clic pour `setActiveTab`, croix pour `closeTab`
- Indicateur de statut de sauvegarde (`saveStatus`) : `saving` → spinner, `saved` → coche, `error` → rouge

---

## Composants transverses

### `src/stores/settings.ts`

Store Pinia pour les préférences utilisateur.

| État | Type | Défaut |
|------|------|--------|
| `username` | string | `'Utilisateur'` |
| `greetingTemplate` | GreetingTemplateId | `'salut'` |
| `greetingRandom` | boolean | `false` |
| `greetingShow` | boolean | `true` |

Actions : `fetchSettings()` → `GET /api/settings/` | `updateSetting(key, value)` → `PUT /api/settings/{key}`

### `src/utils/greeting.ts`

Fonctions pures sans effet de bord.

| Fonction | Description |
|----------|-------------|
| `getTimeOfDay(hour)` | `'matinée'` (5-11h), `'après-midi'` (12-17h), `'soirée'` (18-4h) |
| `getGreetingMessage(templateId, username, hour)` | Génère le message selon le template |
| `getRandomTemplateId()` | Retourne un templateId aléatoire parmi 5 |

### `src/assets/styles/default.css`

Source unique de vérité pour les couleurs. Jamais de couleurs codées en dur dans les composants.

| Variable | Valeur | Usage |
|----------|--------|-------|
| `--color-bg-primary` | `#1a1a2e` | Fond général, toolbar |
| `--color-bg-secondary` | `#16213e` | Panneaux, cards |
| `--color-bg-tertiary` | `#0f3460` | Bordures, hover |
| `--color-accent-primary` | `#e94560` | Accent rouge (actif, focus) |
| `--color-accent-secondary` | — | Accent secondaire |
| `--color-text-primary` | `#eaeaea` | Texte principal |
| `--color-text-secondary` | — | Texte secondaire |
| `--color-text-muted` | — | Texte discret |

---

## Dépendances notables

| Package | Version | Rôle |
|---------|---------|------|
| `@tiptap/vue-3` | ^3.23 | Intégration TipTap pour Vue 3 |
| `@tiptap/starter-kit` | ^3.23 | Extensions de base (headings, listes, undo…) |
| `@tiptap/extension-color` | ^3.23 | Couleur de texte |
| `@tiptap/extension-highlight` | ^3.23 | Surlignage multicolore |
| `@tiptap/extension-text-style` | ^3.23 | Styles inline (requis par Color) |
| `tiptap-markdown` | ^0.9 | Import/export markdown dans TipTap |
| `marked` | ^18 | Rendu markdown (utilisé hors TipTap si besoin) |
| `dompurify` | ^3 | Sanitisation HTML |
| `lucide-vue-next` | ^1.0 | Icônes |
| `pinia` | ^3 | State management |
| `vue-router` | ^4 | Routing |

---

## Lancer en local

```bash
cd frontend

# Frontend uniquement (hot reload, sans Tauri)
npm run dev
# → http://localhost:1420

# Tests unitaires (aucun Docker requis)
npm test
```

> **Prérequis Tauri desktop :** Rust et les dépendances système sont nécessaires pour `npm run tauri dev`. Voir [tauri.app/start/prerequisites](https://tauri.app/start/prerequisites/).

---

## Tests

**23 tests — 0 échec.**

| Suite | Fichier | Tests |
|-------|---------|-------|
| Utils — Greeting | `src/__tests__/greeting.test.ts` | 12 |
| Store — Settings | `src/__tests__/settings.store.test.ts` | 4 |
| Store — Notes | `src/__tests__/notes.store.test.ts` | 7 |

- Tests `greeting.ts` : purement unitaires, pas de DOM ni réseau
- Tests store : `vi.stubGlobal('fetch', ...)` pour simuler l'API
- `setActivePinia(createPinia())` dans `beforeEach` — store frais pour chaque test

---

## Liens

- [→ Référence API](./api-reference.md)
- [→ Plan frontend base](../superpowers/plans/2026-05-01-frontend-base.md)
- [→ Plan module notes](../superpowers/plans/2026-05-03-notes.md)
- [→ Plan explorateur de fichiers](../superpowers/plans/2026-05-08-file-explorer-modal.md)
- [→ Spec explorateur de fichiers](../superpowers/specs/2026-05-08-file-explorer-modal-design.md)
