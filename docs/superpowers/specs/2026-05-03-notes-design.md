# Notes — Design Spec

**Date :** 2026-05-03
**Statut :** Approuvé — prêt pour implémentation

---

## Contexte

Module de prise de notes Markdown intégré à Bobix. Le backend (API + modèles SQLAlchemy) est déjà implémenté. Ce document couvre uniquement le frontend Vue 3.

---

## Architecture des composants

```
NotesView.vue                    ← layout shell (flex row)
├── NotesActionBar.vue           ← panneau gauche étroit
├── div.editor-area              ← zone centrale (flex column)
│   ├── NotesTabs.vue            ← barre d'onglets
│   └── NotesEditor.vue          ← éditeur toggle Éditer / Aperçu
└── BobPanel.vue                 ← panneau droit masquable
```

```
FilesModal.vue                   ← modal explorateur de fichiers
```

**Fichiers à créer :**
- `src/views/NotesView.vue`
- `src/components/notes/NotesActionBar.vue`
- `src/components/notes/NotesTabs.vue`
- `src/components/notes/NotesEditor.vue`
- `src/components/notes/FilesModal.vue`
- `src/components/notes/BobPanel.vue`
- `src/stores/notes.ts`
- `src/__tests__/notes.store.test.ts`

---

## Store — `src/stores/notes.ts`

### État

```typescript
interface NotesState {
  openTabs: Note[]           // notes ouvertes en onglets
  activeTabId: number | null // onglet actif
  isBobVisible: boolean      // panel Bob ouvert/fermé
  pendingContent: string     // contenu en cours (pour auto-save)
  pendingTitle: string       // titre en cours (pour auto-save)
  allNotes: Note[]           // liste complète (pour la modal)
  folders: Folder[]          // arborescence dossiers
}
```

### Actions

| Action | Description |
|--------|-------------|
| `fetchNotes()` | GET /api/notes/ → remplit `allNotes` |
| `fetchFolders()` | GET /api/folders/ → remplit `folders` |
| `openNote(id)` | Si déjà ouvert : setActiveTab. Sinon : GET /api/notes/{id} + push openTabs |
| `closeTab(id)` | Flush auto-save si pendingContent modifié, retire de openTabs |
| `setActiveTab(id)` | Met à jour activeTabId + charge pendingContent |
| `saveNote()` | PATCH /api/notes/{activeTabId} avec titre + contenu |
| `toggleFavorite(id)` | PATCH /api/notes/{id} → toggle is_favorite |
| `createNote(folderId?)` | POST /api/notes/ titre "Sans titre" → ouvre dans onglet |
| `deleteNote(id)` | DELETE /api/notes/{id} → ferme l'onglet si ouvert |
| `createFolder(name, parentId?)` | POST /api/folders/ → rafraîchit `folders` |
| `deleteFolder(id)` | DELETE /api/folders/{id} → rafraîchit `folders` |
| `toggleBob()` | isBobVisible = !isBobVisible |

### Auto-save

- Chaque frappe met à jour `pendingContent` / `pendingTitle`
- Debounce 1s → appel `saveNote()`
- Indicateur dans l'onglet : "Enregistrement..." / "Enregistré" / "Erreur ⚠"
- Retry automatique après 3s en cas d'erreur
- Flush immédiat lors de `closeTab` si modifications en attente

---

## Composants

### NotesActionBar

Panneau gauche étroit (48px de large) avec trois boutons icônes :

| Bouton | Action |
|--------|--------|
| 📁 | Ouvre FilesModal |
| ⭐ | Ouvre FilesModal filtré sur les favoris |
| ✏️ | Crée une nouvelle note (POST /api/notes/) |

### NotesTabs

Barre d'onglets en haut de la zone éditeur.

- Chaque onglet affiche le titre de la note + un indicateur de statut (• si modification en attente) + bouton ✕
- Onglet actif mis en évidence avec `--color-accent-primary`
- Clic sur ✕ → `closeTab(id)`
- Si aucun onglet ouvert → message centré "Ouvre une note depuis 📁"

### NotesEditor

Zone d'édition principale.

**Barre du haut :**
- Titre de la note (input inline, editable)
- Toggle `[✏️ Éditer]` / `[👁 Aperçu]`
- Bouton ⭐ (toggle favori)

**Mode Éditer :**
- `<textarea>` pleine hauteur
- Police monospace (Fira Code, configurable)
- Fond `--color-bg-secondary` pour distinguer du reste

**Mode Aperçu :**
- Rendu HTML via `marked.js` + `DOMPurify`
- Styled avec les variables CSS du thème
- Lecture seule

### FilesModal

Modal plein écran léger (overlay sombre, modal centrée).

**Barre du haut :**
- Titre "Mes fichiers"
- Input recherche (filtre les titres en temps réel, côté client)
- Toggle vue `[≡ Liste]` / `[⊞ Grille]` — préférence sauvegardée en localStorage

**Contenu :**
- Section "⭐ Favoris" en haut (notes avec `is_favorite = true`)
- Arborescence des dossiers avec leurs notes
- Notes sans dossier en bas
- Boutons `[+ note]` et `[+ 📁]` à côté de chaque dossier
- Bouton `[+ Nouvelle note]` en bas de la modal

**Vue liste :** titre + date de modification sur une ligne
**Vue grille :** cartes avec icône 📄 + titre tronqué

Clic sur une note → `openNote(id)` + ferme la modal.

> **Imbrication :** un seul niveau de sous-dossiers supporté dans cette version (dossier → sous-dossier). Le backend supporte `parent_id` pour aller plus loin dans un plan futur.

### BobPanel

Panneau droit (300px), masquable.

- Visible si `isBobVisible = true`
- Bouton toggle dans la barre de NotesEditor
- Contenu : placeholder "Bob — À venir (Plan 6)"
- Quand masqué : l'éditeur prend toute la largeur disponible

---

## Data flow

```
Démarrage NotesView
  → fetchNotes() + fetchFolders()
  → openTabs vide → message "Ouvre une note"

Ouvrir une note
  → si id dans openTabs → setActiveTab(id)
  → sinon → GET /api/notes/{id} → push openTabs → setActiveTab(id)

Édition
  → frappe → pendingContent mis à jour
  → debounce 1s → PATCH /api/notes/{id}
  → succès : indicateur "Enregistré"
  → erreur : indicateur "Erreur ⚠" + retry 3s

Fermer un onglet
  → flush immédiat si modifications en attente
  → retirer de openTabs
  → activer l'onglet précédent (ou vider si aucun)

Nouvelle note
  → POST /api/notes/ { title: "Sans titre" }
  → openNote(newId) → curseur sur le titre

Toggle Bob
  → isBobVisible = !isBobVisible
  → transition CSS sur la largeur de l'éditeur
```

---

## Gestion d'erreurs

| Erreur | Comportement |
|--------|-------------|
| `fetchNotes` échoue | Message "Impossible de charger les notes" dans la modal + bouton réessayer |
| Auto-save échoue | Indicateur "Erreur ⚠" dans l'onglet + retry auto après 3s |
| Note 404 | Ferme l'onglet + toast "Note introuvable" |
| Création échoue | Toast "Erreur lors de la création" |

---

## Tests — `src/__tests__/notes.store.test.ts`

| Test | Description |
|------|-------------|
| état initial correct | openTabs vide, activeTabId null, isBobVisible false |
| openNote — nouvelle note | fetch GET, push openTabs, setActiveTab |
| openNote — déjà ouverte | pas de fetch, juste setActiveTab |
| closeTab — onglet actif | active l'onglet précédent |
| closeTab — dernier onglet | activeTabId → null |
| toggleBob | bascule isBobVisible |
| toggleFavorite | appelle PATCH avec is_favorite inversé |

Tous les tests mockent `fetch` via `vi.stubGlobal` — aucun backend requis.

---

## Dépendances à installer

```bash
npm install marked dompurify
npm install --save-dev @types/dompurify
```

---

## Ce qui est hors scope (implémenté dans un plan futur)

- Panel Bob fonctionnel (Plan 6)
- Dossiers imbriqués au-delà d'un niveau
- Drag & drop des notes entre dossiers
- Export Markdown / PDF
- Raccourcis clavier personnalisables
