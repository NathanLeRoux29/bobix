# File Explorer Modal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign `FilesModal.vue` into a proper file explorer with folder navigation (click-to-enter, breadcrumb), global search, right-click context menu, and HTML5 drag & drop (move + reorder).

**Architecture:** Complete rewrite of `FilesModal.vue` with local navigation state (`currentFolderId`, `navStack`). Three new store actions (`moveNote`, `moveFolder`, `renameFolder`) are added to `stores/notes.ts`. The backend already supports `PATCH /api/folders/{id}` with `name` and `parent_id` fields — no backend changes needed. Drag & drop uses the HTML5 native API with a `localItems` array that tracks display order.

**Tech Stack:** Vue 3 + TypeScript + Pinia + Lucide Vue Next + HTML5 Drag API

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `frontend/src/stores/notes.ts` | Modify | Add `moveNote`, `moveFolder`, `renameFolder` actions |
| `frontend/src/components/notes/FilesModal.vue` | Rewrite | New file explorer: navigation, search, context menu, drag & drop |

---

### Task 1: Add store actions

**Files:**
- Modify: `frontend/src/stores/notes.ts`

- [ ] **Step 1: Add `moveNote`, `moveFolder`, and `renameFolder` to the store**

In `frontend/src/stores/notes.ts`, inside the `actions` object (after `deleteFolder`), add:

```typescript
async moveNote(noteId: number, folderId: number | null) {
  const note = this.allNotes.find((n) => n.id === noteId);
  if (!note) return;
  const prev = note.folder_id;
  note.folder_id = folderId;
  try {
    await fetch(`${API_BASE}/api/notes/${noteId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ folder_id: folderId }),
    });
  } catch {
    note.folder_id = prev;
  }
},

async moveFolder(folderId: number, parentId: number | null) {
  const folder = this.folders.find((f) => f.id === folderId);
  if (!folder) return;
  const prev = folder.parent_id;
  folder.parent_id = parentId;
  try {
    await fetch(`${API_BASE}/api/folders/${folderId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ parent_id: parentId }),
    });
  } catch {
    folder.parent_id = prev;
  }
},

async renameFolder(folderId: number, name: string) {
  const folder = this.folders.find((f) => f.id === folderId);
  if (!folder) return;
  const prev = folder.name;
  folder.name = name;
  try {
    await fetch(`${API_BASE}/api/folders/${folderId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
  } catch {
    folder.name = prev;
  }
},
```

- [ ] **Step 2: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add frontend/src/stores/notes.ts
git commit -m "feat: add moveNote, moveFolder, renameFolder store actions"
```

---

### Task 2: Rewrite FilesModal — navigation shell

**Files:**
- Modify: `frontend/src/components/notes/FilesModal.vue`

Replace the entire file with the content below. This delivers: folder navigation (enter/exit), breadcrumb, global search, click-to-open note. Context menu and drag & drop come in later tasks. The `favoritesOnly` prop shows a flat list of starred notes without folder navigation.

- [ ] **Step 1: Replace FilesModal.vue**

```vue
<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { X, FileText, Folder, Home, Star } from "lucide-vue-next";
import { useNotesStore } from "../../stores/notes";
import type { Folder as FolderType } from "../../types/notes";

const props = defineProps<{ favoritesOnly: boolean }>();
const emit = defineEmits<{ (e: "close"): void }>();

const store = useNotesStore();

// Navigation
const currentFolderId = ref<number | null>(null);
interface NavEntry { id: number | null; name: string }
const navStack = ref<NavEntry[]>([{ id: null, name: "Accueil" }]);

// Search
const searchQuery = ref("");

const currentFolders = computed(() =>
  store.folders.filter((f) => f.parent_id === currentFolderId.value)
);
const currentNotes = computed(() =>
  store.allNotes.filter((n) => n.folder_id === currentFolderId.value)
);

const searchResults = computed(() => {
  const q = searchQuery.value.toLowerCase().trim();
  if (!q) return null;
  if (props.favoritesOnly) {
    return {
      folders: [] as FolderType[],
      notes: store.allNotes.filter(
        (n) => n.is_favorite && (n.title || "Sans titre").toLowerCase().includes(q)
      ),
    };
  }
  return {
    folders: store.folders.filter((f) => f.name.toLowerCase().includes(q)),
    notes: store.allNotes.filter((n) =>
      (n.title || "Sans titre").toLowerCase().includes(q)
    ),
  };
});

const favoriteNotes = computed(() => store.allNotes.filter((n) => n.is_favorite));

function enterFolder(folder: FolderType) {
  currentFolderId.value = folder.id;
  navStack.value = [...navStack.value, { id: folder.id, name: folder.name }];
}

function navigateTo(index: number) {
  navStack.value = navStack.value.slice(0, index + 1);
  currentFolderId.value = navStack.value[index].id;
}

async function selectNote(id: number) {
  await store.openNote(id);
  emit("close");
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close");
}

onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <!-- Header -->
      <div class="modal-header">
        <span class="modal-title">
          <Star v-if="props.favoritesOnly" :size="14" />
          {{ props.favoritesOnly ? "Favoris" : "Fichiers" }}
        </span>
        <button class="close-btn" @click="emit('close')"><X :size="16" /></button>
      </div>

      <!-- Search -->
      <div class="search-bar">
        <input
          v-model="searchQuery"
          class="search-input"
          placeholder="Rechercher..."
          autofocus
        />
      </div>

      <!-- Breadcrumb (normal mode only, hidden during search) -->
      <div v-if="!props.favoritesOnly && !searchQuery" class="breadcrumb">
        <template v-for="(entry, i) in navStack" :key="i">
          <button
            class="breadcrumb-item"
            :class="{ active: i === navStack.length - 1 }"
            @click="navigateTo(i)"
          >
            <Home v-if="i === 0" :size="12" />
            <template v-else>{{ entry.name }}</template>
          </button>
          <span v-if="i < navStack.length - 1" class="breadcrumb-sep">›</span>
        </template>
      </div>

      <!-- Items list -->
      <div class="modal-body">
        <!-- Favorites mode -->
        <template v-if="props.favoritesOnly">
          <template v-if="searchQuery && searchResults">
            <div
              v-for="note in searchResults.notes"
              :key="note.id"
              class="item"
              @click="selectNote(note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <span class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div v-if="!searchResults.notes.length" class="empty">Aucun résultat</div>
          </template>
          <template v-else>
            <div
              v-for="note in favoriteNotes"
              :key="note.id"
              class="item"
              @click="selectNote(note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <span class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div v-if="!favoriteNotes.length" class="empty">Aucun favori</div>
          </template>
        </template>

        <!-- Normal mode -->
        <template v-else>
          <!-- Search results -->
          <template v-if="searchQuery && searchResults">
            <div
              v-for="folder in searchResults.folders"
              :key="'f' + folder.id"
              class="item"
              @click="enterFolder(folder)"
            >
              <Folder :size="14" class="item-icon folder-icon" />
              <span class="item-name">{{ folder.name }}</span>
            </div>
            <div
              v-for="note in searchResults.notes"
              :key="'n' + note.id"
              class="item"
              @click="selectNote(note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <span class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div
              v-if="!searchResults.folders.length && !searchResults.notes.length"
              class="empty"
            >
              Aucun résultat
            </div>
          </template>

          <!-- Current folder contents -->
          <template v-else>
            <div
              v-for="folder in currentFolders"
              :key="'f' + folder.id"
              class="item"
              @click="enterFolder(folder)"
            >
              <Folder :size="14" class="item-icon folder-icon" />
              <span class="item-name">{{ folder.name }}</span>
            </div>
            <div
              v-for="note in currentNotes"
              :key="'n' + note.id"
              class="item"
              @click="selectNote(note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <span class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div v-if="!currentFolders.length && !currentNotes.length" class="empty">
              Ce dossier est vide
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-bg-tertiary);
  border-radius: 8px;
  width: 520px;
  max-height: 65vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-bg-tertiary);
  flex-shrink: 0;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  border-radius: 3px;
  transition: color 0.15s;
}

.close-btn:hover { color: var(--color-text-primary); }

.search-bar {
  padding: 8px 12px;
  border-bottom: 1px solid var(--color-bg-tertiary);
  flex-shrink: 0;
}

.search-input {
  width: 100%;
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-bg-tertiary);
  color: var(--color-text-primary);
  padding: 6px 10px;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
  box-sizing: border-box;
}

.search-input:focus { border-color: var(--color-accent-primary); }

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 6px 12px;
  border-bottom: 1px solid var(--color-bg-tertiary);
  flex-shrink: 0;
  flex-wrap: wrap;
}

.breadcrumb-item {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  font-size: 12px;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  transition: color 0.15s, background-color 0.15s;
}

.breadcrumb-item:hover { color: var(--color-text-primary); background-color: var(--color-bg-tertiary); }
.breadcrumb-item.active { color: var(--color-text-primary); cursor: default; }
.breadcrumb-item.active:hover { background-color: transparent; }

.breadcrumb-sep {
  color: var(--color-text-muted);
  font-size: 12px;
  padding: 0 2px;
  pointer-events: none;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 6px 8px;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.12) transparent;
}

.modal-body::-webkit-scrollbar { width: 5px; }
.modal-body::-webkit-scrollbar-track { background: transparent; }
.modal-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }

.item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.1s;
  user-select: none;
}

.item:hover { background-color: var(--color-bg-tertiary); }

.item-icon { color: var(--color-text-muted); flex-shrink: 0; }
.folder-icon { color: var(--color-accent-secondary); }

.item-name {
  font-size: 13px;
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.empty {
  padding: 24px;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 13px;
}
</style>
```

- [ ] **Step 2: Verify in browser**

Open the app → click "Fichiers":
- Modal shows "Fichiers" title, × closes it, Escape key closes it
- Folders listed first, then notes; clicking a folder enters it
- Breadcrumb shows `Accueil`, clicking a breadcrumb segment navigates back
- Typing in search shows global results; clearing search restores current folder
- Clicking a note opens it in a tab and closes the modal

Open via "Ouvrir les favoris":
- Modal shows "Favoris" title with star icon, no breadcrumb
- Only favorite notes are listed; search filters within them

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/notes/FilesModal.vue
git commit -m "feat: rewrite FilesModal with folder navigation and search"
```

---

### Task 3: Add context menu, rename, and folder creation

**Files:**
- Modify: `frontend/src/components/notes/FilesModal.vue`

- [ ] **Step 1: Add state and handlers to `<script setup>`**

After `onMounted`/`onUnmounted`, add:

```typescript
// Rename state
const renamingNoteId = ref<number | null>(null);
const renamingFolderId = ref<number | null>(null);
const renameValue = ref("");

// New folder inline input (false = hidden, null = root, number = parent id)
const newFolderParentId = ref<number | null | false>(false);
const newFolderName = ref("");

// Context menu
interface CtxMenu {
  x: number;
  y: number;
  kind: "note" | "folder" | "background";
  noteId?: number;
  folderId?: number;
}
const contextMenu = ref<CtxMenu | null>(null);

function openCtx(e: MouseEvent, kind: "note" | "folder" | "background", id?: number) {
  e.preventDefault();
  e.stopPropagation();
  const x = Math.min(e.clientX, window.innerWidth - 180);
  const y = Math.min(e.clientY, window.innerHeight - 180);
  contextMenu.value = {
    x, y, kind,
    noteId: kind === "note" ? id : undefined,
    folderId: kind === "folder" ? id : undefined,
  };
}

function closeCtx() { contextMenu.value = null; }

function startRenameNote(id: number) {
  const note = store.allNotes.find((n) => n.id === id);
  if (!note) return;
  renamingNoteId.value = id;
  renamingFolderId.value = null;
  renameValue.value = note.title;
  closeCtx();
}

async function submitRenameNote(id: number) {
  if (renameValue.value.trim()) await store.renameNote(id, renameValue.value.trim());
  renamingNoteId.value = null;
}

function startRenameFolder(id: number) {
  const folder = store.folders.find((f) => f.id === id);
  if (!folder) return;
  renamingFolderId.value = id;
  renamingNoteId.value = null;
  renameValue.value = folder.name;
  closeCtx();
}

async function submitRenameFolder(id: number) {
  if (renameValue.value.trim()) await store.renameFolder(id, renameValue.value.trim());
  renamingFolderId.value = null;
}

function showNewFolder(parentId: number | null) {
  newFolderParentId.value = parentId;
  newFolderName.value = "";
  closeCtx();
}

async function submitNewFolder() {
  if (!newFolderName.value.trim()) { newFolderParentId.value = false; return; }
  const parentId = typeof newFolderParentId.value === "number"
    ? newFolderParentId.value
    : undefined;
  await store.createFolder(newFolderName.value.trim(), parentId);
  newFolderName.value = "";
  newFolderParentId.value = false;
}

async function ctxCreateNoteInFolder(folderId: number) {
  await store.createNote(folderId);
  emit("close");
}

async function ctxCreateNoteHere() {
  await store.createNote(currentFolderId.value ?? undefined);
  emit("close");
}

async function ctxDeleteNote(noteId: number) {
  await store.deleteNote(noteId);
  closeCtx();
}

async function ctxDeleteFolder(folderId: number) {
  await store.deleteFolder(folderId);
  closeCtx();
}
```

- [ ] **Step 2: Update `onMounted`/`onUnmounted` to close context menu on outside click**

Replace:
```typescript
onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));
```

With:
```typescript
onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  document.addEventListener("click", closeCtx);
});
onUnmounted(() => {
  document.removeEventListener("keydown", onKeydown);
  document.removeEventListener("click", closeCtx);
});
```

- [ ] **Step 3: Guard `selectNote` and `enterFolder` against rename clicks**

Replace:
```typescript
async function selectNote(id: number) {
  await store.openNote(id);
  emit("close");
}
```
With:
```typescript
async function selectNote(id: number) {
  if (renamingNoteId.value === id) return;
  await store.openNote(id);
  emit("close");
}
```

Replace:
```typescript
function enterFolder(folder: FolderType) {
  currentFolderId.value = folder.id;
  navStack.value = [...navStack.value, { id: folder.id, name: folder.name }];
}
```
With:
```typescript
function enterFolder(folder: FolderType) {
  if (renamingFolderId.value === folder.id) return;
  currentFolderId.value = folder.id;
  navStack.value = [...navStack.value, { id: folder.id, name: folder.name }];
}
```

- [ ] **Step 4: Update the template**

Replace the entire `<template>` block with:

```html
<template>
  <div class="modal-overlay" @click.self="emit('close')">
    <div class="modal">
      <!-- Header -->
      <div class="modal-header">
        <span class="modal-title">
          <Star v-if="props.favoritesOnly" :size="14" />
          {{ props.favoritesOnly ? "Favoris" : "Fichiers" }}
        </span>
        <button class="close-btn" @click="emit('close')"><X :size="16" /></button>
      </div>

      <!-- Search -->
      <div class="search-bar">
        <input
          v-model="searchQuery"
          class="search-input"
          placeholder="Rechercher..."
          autofocus
        />
      </div>

      <!-- Breadcrumb -->
      <div v-if="!props.favoritesOnly && !searchQuery" class="breadcrumb">
        <template v-for="(entry, i) in navStack" :key="i">
          <button
            class="breadcrumb-item"
            :class="{ active: i === navStack.length - 1 }"
            @click="navigateTo(i)"
          >
            <Home v-if="i === 0" :size="12" />
            <template v-else>{{ entry.name }}</template>
          </button>
          <span v-if="i < navStack.length - 1" class="breadcrumb-sep">›</span>
        </template>
      </div>

      <!-- New folder inline input -->
      <div v-if="newFolderParentId !== false" class="new-folder-bar">
        <Folder :size="13" />
        <input
          v-model="newFolderName"
          class="new-folder-input"
          placeholder="Nom du dossier"
          autofocus
          @keyup.enter="submitNewFolder"
          @keyup.esc="newFolderParentId = false"
          @blur="submitNewFolder"
        />
      </div>

      <!-- Items list -->
      <div class="modal-body" @contextmenu="openCtx($event, 'background')">
        <!-- Favorites mode -->
        <template v-if="props.favoritesOnly">
          <template v-if="searchQuery && searchResults">
            <div
              v-for="note in searchResults.notes"
              :key="note.id"
              class="item"
              @click="selectNote(note.id)"
              @contextmenu.stop="openCtx($event, 'note', note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <template v-if="renamingNoteId === note.id">
                <input v-model="renameValue" class="rename-input" autofocus @click.stop
                  @keyup.enter="submitRenameNote(note.id)" @keyup.esc="renamingNoteId = null"
                  @blur="submitRenameNote(note.id)" />
              </template>
              <span v-else class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div v-if="!searchResults.notes.length" class="empty">Aucun résultat</div>
          </template>
          <template v-else>
            <div
              v-for="note in favoriteNotes"
              :key="note.id"
              class="item"
              @click="selectNote(note.id)"
              @contextmenu.stop="openCtx($event, 'note', note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <template v-if="renamingNoteId === note.id">
                <input v-model="renameValue" class="rename-input" autofocus @click.stop
                  @keyup.enter="submitRenameNote(note.id)" @keyup.esc="renamingNoteId = null"
                  @blur="submitRenameNote(note.id)" />
              </template>
              <span v-else class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div v-if="!favoriteNotes.length" class="empty">Aucun favori</div>
          </template>
        </template>

        <!-- Normal mode -->
        <template v-else>
          <!-- Search results -->
          <template v-if="searchQuery && searchResults">
            <div
              v-for="folder in searchResults.folders"
              :key="'f' + folder.id"
              class="item"
              @click="enterFolder(folder)"
              @contextmenu.stop="openCtx($event, 'folder', folder.id)"
            >
              <Folder :size="14" class="item-icon folder-icon" />
              <template v-if="renamingFolderId === folder.id">
                <input v-model="renameValue" class="rename-input" autofocus @click.stop
                  @keyup.enter="submitRenameFolder(folder.id)" @keyup.esc="renamingFolderId = null"
                  @blur="submitRenameFolder(folder.id)" />
              </template>
              <span v-else class="item-name">{{ folder.name }}</span>
            </div>
            <div
              v-for="note in searchResults.notes"
              :key="'n' + note.id"
              class="item"
              @click="selectNote(note.id)"
              @contextmenu.stop="openCtx($event, 'note', note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <template v-if="renamingNoteId === note.id">
                <input v-model="renameValue" class="rename-input" autofocus @click.stop
                  @keyup.enter="submitRenameNote(note.id)" @keyup.esc="renamingNoteId = null"
                  @blur="submitRenameNote(note.id)" />
              </template>
              <span v-else class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div
              v-if="!searchResults.folders.length && !searchResults.notes.length"
              class="empty"
            >
              Aucun résultat
            </div>
          </template>

          <!-- Current folder contents -->
          <template v-else>
            <div
              v-for="folder in currentFolders"
              :key="'f' + folder.id"
              class="item"
              @click="enterFolder(folder)"
              @contextmenu.stop="openCtx($event, 'folder', folder.id)"
            >
              <Folder :size="14" class="item-icon folder-icon" />
              <template v-if="renamingFolderId === folder.id">
                <input v-model="renameValue" class="rename-input" autofocus @click.stop
                  @keyup.enter="submitRenameFolder(folder.id)" @keyup.esc="renamingFolderId = null"
                  @blur="submitRenameFolder(folder.id)" />
              </template>
              <span v-else class="item-name">{{ folder.name }}</span>
            </div>
            <div
              v-for="note in currentNotes"
              :key="'n' + note.id"
              class="item"
              @click="selectNote(note.id)"
              @contextmenu.stop="openCtx($event, 'note', note.id)"
            >
              <FileText :size="14" class="item-icon" />
              <template v-if="renamingNoteId === note.id">
                <input v-model="renameValue" class="rename-input" autofocus @click.stop
                  @keyup.enter="submitRenameNote(note.id)" @keyup.esc="renamingNoteId = null"
                  @blur="submitRenameNote(note.id)" />
              </template>
              <span v-else class="item-name">{{ note.title || "Sans titre" }}</span>
            </div>
            <div v-if="!currentFolders.length && !currentNotes.length" class="empty">
              Ce dossier est vide
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>

  <!-- Context menu (Teleport prevents clipping) -->
  <Teleport to="body">
    <div
      v-if="contextMenu"
      class="ctx-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <template v-if="contextMenu.kind === 'note' && contextMenu.noteId !== undefined">
        <button class="ctx-item" @click="startRenameNote(contextMenu.noteId)">Renommer</button>
        <div class="ctx-separator" />
        <button class="ctx-item danger" @click="ctxDeleteNote(contextMenu.noteId)">Supprimer</button>
      </template>

      <template v-else-if="contextMenu.kind === 'folder' && contextMenu.folderId !== undefined">
        <button class="ctx-item" @click="ctxCreateNoteInFolder(contextMenu.folderId)">Nouvelle note</button>
        <button class="ctx-item" @click="showNewFolder(contextMenu.folderId)">Nouveau sous-dossier</button>
        <div class="ctx-separator" />
        <button class="ctx-item" @click="startRenameFolder(contextMenu.folderId)">Renommer</button>
        <button class="ctx-item danger" @click="ctxDeleteFolder(contextMenu.folderId)">Supprimer</button>
      </template>

      <template v-else>
        <button class="ctx-item" @click="ctxCreateNoteHere">Nouvelle note</button>
        <button class="ctx-item" @click="showNewFolder(currentFolderId)">Nouveau dossier</button>
      </template>
    </div>
  </Teleport>
</template>
```

- [ ] **Step 5: Add styles for new folder bar, rename input, and context menu**

Add to `<style scoped>`:

```css
.new-folder-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-bottom: 1px solid var(--color-bg-tertiary);
  background-color: var(--color-bg-primary);
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.new-folder-input {
  flex: 1;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--color-accent-primary);
  color: var(--color-text-primary);
  padding: 2px 4px;
  font-size: 13px;
  outline: none;
}

.rename-input {
  flex: 1;
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-accent-primary);
  color: var(--color-text-primary);
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
  outline: none;
  min-width: 0;
}
```

Add a non-scoped `<style>` block at the bottom of the file:

```css
.ctx-menu {
  position: fixed;
  z-index: 9999;
  background-color: #1e2a3a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 4px;
  min-width: 170px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}

.ctx-item {
  display: block;
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  color: #d0d0d0;
  padding: 7px 12px;
  font-size: 13px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.1s, color 0.1s;
}

.ctx-item:hover { background-color: rgba(255, 255, 255, 0.08); color: #ffffff; }
.ctx-item.danger { color: #ef4444; }
.ctx-item.danger:hover { background-color: rgba(239, 68, 68, 0.12); }

.ctx-separator {
  height: 1px;
  background-color: rgba(255, 255, 255, 0.08);
  margin: 3px 4px;
}
```

- [ ] **Step 6: Verify in browser**

- Right-click a note → "Renommer" shows inline input; Enter submits, Escape cancels; "Supprimer" deletes
- Right-click a folder → "Nouvelle note" creates note and closes modal; "Nouveau sous-dossier" shows inline input; "Renommer" edits folder name; "Supprimer" deletes folder
- Right-click empty area → "Nouvelle note" creates in current folder; "Nouveau dossier" shows inline input
- Menu closes when clicking outside

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/notes/FilesModal.vue
git commit -m "feat: add context menu, rename, and folder creation to FilesModal"
```

---

### Task 4: Add drag & drop

**Files:**
- Modify: `frontend/src/components/notes/FilesModal.vue`

- [ ] **Step 1: Add imports and drag state to `<script setup>`**

Add `watch` to the Vue import (it's likely already imported, just ensure it's there):
```typescript
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
```

Also add `Note` to the type import:
```typescript
import type { Folder as FolderType, Note } from "../../types/notes";
```

After the `newFolderParentId` / `newFolderName` declarations, add:

```typescript
// Drag & drop
interface DragItem { type: "note" | "folder"; id: number }
const dragItem = ref<DragItem | null>(null);
const dragOverFolderId = ref<number | null>(null);
const insertionIndex = ref<number | null>(null);

// Combined ordered list for current folder (enables reordering)
interface LocalItem { type: "note" | "folder"; id: number }
const localItems = ref<LocalItem[]>([]);

function buildLocalItems() {
  const folders = currentFolders.value.map((f): LocalItem => ({ type: "folder", id: f.id }));
  const notes = currentNotes.value.map((n): LocalItem => ({ type: "note", id: n.id }));
  const combined = [...folders, ...notes];
  const preserved = localItems.value.filter((p) =>
    combined.some((c) => c.type === p.type && c.id === p.id)
  );
  const added = combined.filter((c) =>
    !localItems.value.some((p) => p.type === c.type && p.id === c.id)
  );
  localItems.value = [...preserved, ...added];
}

watch([currentFolderId, currentFolders, currentNotes], buildLocalItems, { immediate: true });

const displayItems = computed(() =>
  localItems.value
    .map((item) => {
      if (item.type === "folder") {
        const data = store.folders.find((f) => f.id === item.id);
        return data ? { type: "folder" as const, id: item.id, data } : null;
      } else {
        const data = store.allNotes.find((n) => n.id === item.id);
        return data ? { type: "note" as const, id: item.id, data } : null;
      }
    })
    .filter((x): x is NonNullable<typeof x> => x !== null)
);

function isDescendant(potentialDescendantId: number, ancestorId: number): boolean {
  let folder = store.folders.find((f) => f.id === potentialDescendantId);
  while (folder && folder.parent_id !== null) {
    if (folder.parent_id === ancestorId) return true;
    folder = store.folders.find((f) => f.id === folder!.parent_id);
  }
  return false;
}

function onDragStart(e: DragEvent, item: DragItem) {
  dragItem.value = item;
  if (e.dataTransfer) e.dataTransfer.effectAllowed = "move";
}

function onDragEnd() {
  dragItem.value = null;
  dragOverFolderId.value = null;
  insertionIndex.value = null;
}

function onDragOverFolder(e: DragEvent, folderId: number) {
  if (!dragItem.value) return;
  if (dragItem.value.type === "folder") {
    if (dragItem.value.id === folderId || isDescendant(folderId, dragItem.value.id)) return;
  }
  e.preventDefault();
  dragOverFolderId.value = folderId;
  insertionIndex.value = null;
  if (e.dataTransfer) e.dataTransfer.dropEffect = "move";
}

function onDragLeaveFolder() {
  dragOverFolderId.value = null;
}

function onDragOverGap(e: DragEvent, index: number) {
  e.preventDefault();
  dragOverFolderId.value = null;
  insertionIndex.value = index;
  if (e.dataTransfer) e.dataTransfer.dropEffect = "move";
}

async function onDropOnFolder(folderId: number) {
  if (!dragItem.value) return;
  const item = dragItem.value;
  if (item.type === "folder") {
    if (item.id === folderId || isDescendant(folderId, item.id)) return;
    localItems.value = localItems.value.filter((i) => !(i.type === "folder" && i.id === item.id));
    await store.moveFolder(item.id, folderId);
  } else {
    localItems.value = localItems.value.filter((i) => !(i.type === "note" && i.id === item.id));
    await store.moveNote(item.id, folderId);
  }
  dragItem.value = null;
  dragOverFolderId.value = null;
}

function onDropReorder() {
  if (!dragItem.value || insertionIndex.value === null) return;
  const items = [...localItems.value];
  const fromIndex = items.findIndex(
    (i) => i.type === dragItem.value!.type && i.id === dragItem.value!.id
  );
  if (fromIndex === -1) return;
  const [moved] = items.splice(fromIndex, 1);
  let target = insertionIndex.value;
  if (target > fromIndex) target--;
  items.splice(target, 0, moved);
  localItems.value = items;
  dragItem.value = null;
  insertionIndex.value = null;
}
```

- [ ] **Step 2: Replace the "Current folder contents" block in the template**

In the template, find the `<template v-else>` block that renders `currentFolders` and `currentNotes` (under "Current folder contents" comment) and replace it with the drag-aware version:

```html
<!-- Current folder contents (drag & drop enabled) -->
<template v-else>
  <div
    class="insertion-line"
    :class="{ visible: insertionIndex === 0 }"
    @dragover.prevent="onDragOverGap($event, 0)"
    @drop.prevent="onDropReorder"
  />

  <template v-for="(item, i) in displayItems" :key="item.type + item.id">
    <!-- Folder -->
    <div
      v-if="item.type === 'folder'"
      class="item"
      :class="{
        'drag-over-folder': dragOverFolderId === item.id,
        dragging: dragItem?.type === 'folder' && dragItem?.id === item.id,
      }"
      draggable="true"
      @dragstart="onDragStart($event, { type: 'folder', id: item.id })"
      @dragend="onDragEnd"
      @dragover="onDragOverFolder($event, item.id)"
      @dragleave="onDragLeaveFolder"
      @drop.prevent="onDropOnFolder(item.id)"
      @click="enterFolder(item.data as FolderType)"
      @contextmenu.stop="openCtx($event, 'folder', item.id)"
    >
      <Folder :size="14" class="item-icon folder-icon" />
      <template v-if="renamingFolderId === item.id">
        <input v-model="renameValue" class="rename-input" autofocus @click.stop
          @keyup.enter="submitRenameFolder(item.id)" @keyup.esc="renamingFolderId = null"
          @blur="submitRenameFolder(item.id)" />
      </template>
      <span v-else class="item-name">{{ (item.data as FolderType).name }}</span>
    </div>

    <!-- Note -->
    <div
      v-else
      class="item"
      :class="{ dragging: dragItem?.type === 'note' && dragItem?.id === item.id }"
      draggable="true"
      @dragstart="onDragStart($event, { type: 'note', id: item.id })"
      @dragend="onDragEnd"
      @click="selectNote(item.id)"
      @contextmenu.stop="openCtx($event, 'note', item.id)"
    >
      <FileText :size="14" class="item-icon" />
      <template v-if="renamingNoteId === item.id">
        <input v-model="renameValue" class="rename-input" autofocus @click.stop
          @keyup.enter="submitRenameNote(item.id)" @keyup.esc="renamingNoteId = null"
          @blur="submitRenameNote(item.id)" />
      </template>
      <span v-else class="item-name">{{ (item.data as Note).title || "Sans titre" }}</span>
    </div>

    <!-- Insertion line after each item -->
    <div
      class="insertion-line"
      :class="{ visible: insertionIndex === i + 1 }"
      @dragover.prevent="onDragOverGap($event, i + 1)"
      @drop.prevent="onDropReorder"
    />
  </template>

  <div v-if="displayItems.length === 0" class="empty">Ce dossier est vide</div>
</template>
```

- [ ] **Step 3: Add drag & drop styles to `<style scoped>`**

```css
.item.dragging {
  opacity: 0.4;
}

.item.drag-over-folder {
  background-color: rgba(99, 179, 237, 0.12);
  outline: 1px solid var(--color-accent-primary);
  outline-offset: -1px;
}

.insertion-line {
  height: 8px;
  margin: -3px 8px;
  position: relative;
  pointer-events: auto;
}

.insertion-line::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 3px;
  height: 2px;
  border-radius: 1px;
  background-color: transparent;
  transition: background-color 0.1s;
}

.insertion-line.visible::after {
  background-color: var(--color-accent-primary);
}
```

- [ ] **Step 4: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: no errors

- [ ] **Step 5: Verify in browser**

- Drag a note onto a folder → note disappears from current view (moved into the folder); entering the folder shows the moved note
- Drag a folder onto another folder → folder disappears (moved inside the target)
- Drag a folder over one of its own subfolders → no highlight, no drop (blocked)
- Drag an item between two others → blue insertion line appears; on drop the item reorders
- The dragged item is semi-transparent during drag
- After dropping, context menu and clicks still work normally

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/notes/FilesModal.vue
git commit -m "feat: add drag & drop to file explorer modal"
```
