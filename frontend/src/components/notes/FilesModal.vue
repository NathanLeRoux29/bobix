<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from "vue";
import { X, FileText, Folder, Home, Star, List, LayoutGrid } from "lucide-vue-next";
import { useNotesStore } from "../../stores/notes";
import type { Folder as FolderType, Note } from "../../types/notes";

const props = defineProps<{ favoritesOnly: boolean }>();
const emit = defineEmits<{ (e: "close"): void }>();

const store = useNotesStore();

// View mode
const viewMode = ref<"list" | "grid">(
  (localStorage.getItem("notes-view-mode") as "list" | "grid") ?? "list"
);
function setViewMode(mode: "list" | "grid") {
  viewMode.value = mode;
  localStorage.setItem("notes-view-mode", mode);
}

// Navigation
const currentFolderId = ref<number | null>(null);
interface NavEntry { id: number | null; name: string }
const navStack = ref<NavEntry[]>([{ id: null, name: "Accueil" }]);

// Search
const searchQuery = ref("");

// Multi-select
const selectedItems = ref<Set<string>>(new Set());
let longPressTimer: ReturnType<typeof setTimeout> | null = null;
let longPressActivated = false;
let lastSelectedIndex = -1;

const hasSelection = computed(() => selectedItems.value.size > 0);
const selectedNoteCount = computed(
  () => [...selectedItems.value].filter((k) => k.startsWith("note:")).length
);

function itemKey(type: "note" | "folder", id: number) {
  return `${type}:${id}`;
}
function isSelected(type: "note" | "folder", id: number) {
  return selectedItems.value.has(itemKey(type, id));
}
function toggleSelect(type: "note" | "folder", id: number) {
  const key = itemKey(type, id);
  const next = new Set(selectedItems.value);
  if (next.has(key)) next.delete(key);
  else next.add(key);
  selectedItems.value = next;
}
function clearSelection() {
  selectedItems.value = new Set();
}

// Clipboard (notes only)
interface ClipboardItem { type: "note"; id: number }
const clipboard = ref<ClipboardItem[]>([]);
const canPaste = computed(() => clipboard.value.length > 0);

// Current folder
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

// Navigation
function enterFolder(folder: FolderType) {
  if (renamingFolderId.value === folder.id) return;
  currentFolderId.value = folder.id;
  navStack.value = [...navStack.value, { id: folder.id, name: folder.name }];
}

function navigateTo(index: number) {
  navStack.value = navStack.value.slice(0, index + 1);
  currentFolderId.value = navStack.value[index].id;
}

async function selectNote(id: number) {
  if (renamingNoteId.value === id) return;
  await store.openNote(id);
  emit("close");
}

// Click handlers with selection + range (Shift)
function onDisplayItemClick(e: MouseEvent, type: "note" | "folder", id: number, index: number) {
  if (longPressActivated) { longPressActivated = false; return; }
  if (type === "note" && renamingNoteId.value === id) return;
  if (type === "folder" && renamingFolderId.value === id) return;

  if (e.shiftKey && lastSelectedIndex >= 0) {
    const start = Math.min(lastSelectedIndex, index);
    const end = Math.max(lastSelectedIndex, index);
    const next = new Set(selectedItems.value);
    for (let i = start; i <= end; i++) {
      const item = displayItems.value[i];
      if (item) next.add(itemKey(item.type, item.id));
    }
    selectedItems.value = next;
    return;
  }

  if (e.ctrlKey || e.metaKey || hasSelection.value) {
    lastSelectedIndex = index;
    toggleSelect(type, id);
    return;
  }

  lastSelectedIndex = index;
  if (type === "note") selectNote(id);
  else {
    const folder = store.folders.find((f) => f.id === id);
    if (folder) enterFolder(folder);
  }
}

// For search/favorites (no index-based range)
function onSimpleItemClick(e: MouseEvent, type: "note" | "folder", id: number) {
  if (longPressActivated) { longPressActivated = false; return; }
  if (type === "note" && renamingNoteId.value === id) return;
  if (type === "folder" && renamingFolderId.value === id) return;
  if (e.ctrlKey || e.metaKey || e.shiftKey || hasSelection.value) {
    toggleSelect(type, id);
    return;
  }
  if (type === "note") selectNote(id);
  else {
    const folder = store.folders.find((f) => f.id === id);
    if (folder) enterFolder(folder);
  }
}

function onFolderDblClick(folder: FolderType) {
  clearSelection();
  enterFolder(folder);
}

// Long press
function onItemMouseDown(type: "note" | "folder", id: number) {
  longPressActivated = false;
  longPressTimer = setTimeout(() => {
    longPressActivated = true;
    toggleSelect(type, id);
    longPressTimer = null;
  }, 300);
}

function cancelLongPress() {
  if (longPressTimer) {
    clearTimeout(longPressTimer);
    longPressTimer = null;
  }
}

// Rename state
const renamingNoteId = ref<number | null>(null);
const renamingFolderId = ref<number | null>(null);
const renameValue = ref("");

// New folder
const newFolderParentId = ref<number | null | false>(false);
const newFolderName = ref("");

// Context menu
interface CtxMenu {
  x: number;
  y: number;
  kind: "note" | "folder" | "background" | "multiselect";
  noteId?: number;
  folderId?: number;
  inFavorites?: boolean;
}
const contextMenu = ref<CtxMenu | null>(null);

function openCtx(e: MouseEvent, kind: "note" | "folder" | "background", id?: number) {
  e.preventDefault();
  e.stopPropagation();
  const x = Math.min(e.clientX, window.innerWidth - 190);
  const y = Math.min(e.clientY, window.innerHeight - 210);
  if (hasSelection.value && id !== undefined && (kind === "note" || kind === "folder")) {
    const key = itemKey(kind, id);
    if (selectedItems.value.has(key) && selectedItems.value.size > 1) {
      contextMenu.value = { x, y, kind: "multiselect" };
      return;
    }
  }
  contextMenu.value = {
    x, y, kind,
    noteId: kind === "note" ? id : undefined,
    folderId: kind === "folder" ? id : undefined,
    inFavorites: props.favoritesOnly && kind === "note",
  };
}

function closeCtx() { contextMenu.value = null; }

// Rename
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

// Folder creation
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

// Context menu actions
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
async function ctxRemoveFromFavorites(noteId: number) {
  await store.toggleFavorite(noteId);
  closeCtx();
}

async function ctxDeleteSelection() {
  for (const key of [...selectedItems.value]) {
    const [type, idStr] = key.split(":");
    const id = Number(idStr);
    if (type === "note") await store.deleteNote(id);
    else if (type === "folder") await store.deleteFolder(id);
  }
  clearSelection();
  closeCtx();
}

// Copy/paste
function uniqueTitle(baseTitle: string): string {
  const titles = new Set(store.allNotes.map((n) => n.title));
  if (!titles.has(baseTitle)) return baseTitle;
  let i = 1;
  while (titles.has(`${baseTitle} (${i})`)) i++;
  return `${baseTitle} (${i})`;
}
function copySingleNote(noteId: number) {
  clipboard.value = [{ type: "note", id: noteId }];
  closeCtx();
}
function copySelection() {
  clipboard.value = [...selectedItems.value]
    .filter((k) => k.startsWith("note:"))
    .map((k) => ({ type: "note" as const, id: Number(k.split(":")[1]) }));
  closeCtx();
}
async function pasteItems() {
  for (const item of clipboard.value) {
    const note = store.allNotes.find((n) => n.id === item.id);
    if (!note) continue;
    const title = uniqueTitle(note.title || "Sans titre");
    await store.copyNote(item.id, currentFolderId.value, title);
  }
  closeCtx();
}

// Drag & drop
interface DragItem { type: "note" | "folder"; id: number }
const dragItem = ref<DragItem | null>(null);
const dragOverFolderId = ref<number | null>(null);
const insertionIndex = ref<number | null>(null);
const dragOverBreadcrumbIndex = ref<number | null>(null);

// Local ordered list for current folder
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

function getItemsToMove(): DragItem[] {
  if (!dragItem.value) return [];
  if (isSelected(dragItem.value.type, dragItem.value.id) && hasSelection.value) {
    return [...selectedItems.value].map((key) => {
      const [type, idStr] = key.split(":");
      return { type: type as "note" | "folder", id: Number(idStr) };
    });
  }
  return [dragItem.value];
}

async function performMove(items: DragItem[], targetFolderId: number | null) {
  for (const item of items) {
    if (item.type === "folder") {
      if (targetFolderId !== null && (item.id === targetFolderId || isDescendant(targetFolderId, item.id))) continue;
      localItems.value = localItems.value.filter((i) => !(i.type === "folder" && i.id === item.id));
      await store.moveFolder(item.id, targetFolderId);
    } else {
      localItems.value = localItems.value.filter((i) => !(i.type === "note" && i.id === item.id));
      await store.moveNote(item.id, targetFolderId);
    }
  }
}

function onDragStart(e: DragEvent, item: DragItem) {
  cancelLongPress();
  dragItem.value = item;
  if (e.dataTransfer) e.dataTransfer.effectAllowed = "move";
}

function onDragEnd() {
  dragItem.value = null;
  dragOverFolderId.value = null;
  insertionIndex.value = null;
  dragOverBreadcrumbIndex.value = null;
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
  const items = getItemsToMove();
  await performMove(items, folderId);
  if (items.some((i) => isSelected(i.type, i.id))) clearSelection();
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

function onDragOverBreadcrumb(e: DragEvent, index: number) {
  if (!dragItem.value) return;
  if (index === navStack.value.length - 1) return; // current folder — not a valid target
  e.preventDefault();
  dragOverBreadcrumbIndex.value = index;
  if (e.dataTransfer) e.dataTransfer.dropEffect = "move";
}

function onDragLeaveBreadcrumb(e: DragEvent) {
  const related = e.relatedTarget as Node | null;
  if (related && (e.currentTarget as HTMLElement)?.contains(related)) return;
  dragOverBreadcrumbIndex.value = null;
}

async function onDropOnBreadcrumb(targetFolderId: number | null) {
  if (!dragItem.value) return;
  if (targetFolderId === currentFolderId.value) return; // already in this folder
  const items = getItemsToMove();
  await performMove(items, targetFolderId);
  if (items.some((i) => isSelected(i.type, i.id))) clearSelection();
  dragItem.value = null;
  dragOverBreadcrumbIndex.value = null;
}

// Keyboard
function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") {
    if (hasSelection.value) { clearSelection(); return; }
    emit("close");
    return;
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "c") {
    if (hasSelection.value) copySelection();
    return;
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "v") {
    if (canPaste.value) pasteItems();
    return;
  }
}

onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  document.addEventListener("click", closeCtx);
  document.addEventListener("mouseup", cancelLongPress);
});
onUnmounted(() => {
  document.removeEventListener("keydown", onKeydown);
  document.removeEventListener("click", closeCtx);
  document.removeEventListener("mouseup", cancelLongPress);
});
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
        <div class="modal-controls">
          <span v-if="hasSelection" class="selection-count">{{ selectedItems.size }} sélectionné(s)</span>
          <button class="view-btn" :class="{ active: viewMode === 'list' }" title="Vue liste" @click="setViewMode('list')">
            <List :size="14" />
          </button>
          <button class="view-btn" :class="{ active: viewMode === 'grid' }" title="Vue grille" @click="setViewMode('grid')">
            <LayoutGrid :size="14" />
          </button>
          <button class="close-btn" @click="emit('close')"><X :size="16" /></button>
        </div>
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

      <!-- Breadcrumb (normal mode, hidden during search) -->
      <div v-if="!props.favoritesOnly && !searchQuery" class="breadcrumb">
        <template v-for="(entry, i) in navStack" :key="i">
          <button
            class="breadcrumb-item"
            :class="{ active: i === navStack.length - 1, 'drag-over': dragOverBreadcrumbIndex === i }"
            @click="navigateTo(i)"
            @dragover="onDragOverBreadcrumb($event, i)"
            @dragleave="onDragLeaveBreadcrumb($event)"
            @drop.prevent="onDropOnBreadcrumb(entry.id)"
          >
            <Home v-if="i === 0" :size="12" />
            {{ entry.name }}
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
      <div class="modal-body" :class="viewMode" @click.self="clearSelection" @contextmenu="openCtx($event, 'background')">

        <!-- Favorites mode -->
        <template v-if="props.favoritesOnly">
          <template v-if="searchQuery && searchResults">
            <div v-for="note in searchResults.notes" :key="note.id" class="item"
              :class="{ selected: isSelected('note', note.id) }"
              @mousedown="onItemMouseDown('note', note.id)"
              @click="onSimpleItemClick($event, 'note', note.id)"
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
            <div v-for="note in favoriteNotes" :key="note.id" class="item"
              :class="{ selected: isSelected('note', note.id) }"
              @mousedown="onItemMouseDown('note', note.id)"
              @click="onSimpleItemClick($event, 'note', note.id)"
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
            <div v-for="folder in searchResults.folders" :key="'f' + folder.id" class="item"
              :class="{ selected: isSelected('folder', folder.id) }"
              @mousedown="onItemMouseDown('folder', folder.id)"
              @click="onSimpleItemClick($event, 'folder', folder.id)"
              @dblclick="onFolderDblClick(folder)"
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
            <div v-for="note in searchResults.notes" :key="'n' + note.id" class="item"
              :class="{ selected: isSelected('note', note.id) }"
              @mousedown="onItemMouseDown('note', note.id)"
              @click="onSimpleItemClick($event, 'note', note.id)"
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
            <div v-if="!searchResults.folders.length && !searchResults.notes.length" class="empty">Aucun résultat</div>
          </template>

          <!-- Current folder (drag & drop + multi-select) -->
          <template v-else>
            <div class="insertion-line" :class="{ visible: insertionIndex === 0 }"
              @dragover.prevent="onDragOverGap($event, 0)" @drop.prevent="onDropReorder" />

            <template v-for="(item, i) in displayItems" :key="item.type + item.id">
              <!-- Folder -->
              <div v-if="item.type === 'folder'" class="item"
                :class="{
                  'drag-over-folder': dragOverFolderId === item.id,
                  dragging: dragItem?.type === 'folder' && dragItem?.id === item.id,
                  selected: isSelected('folder', item.id),
                }"
                draggable="true"
                @mousedown="onItemMouseDown('folder', item.id)"
                @dragstart="onDragStart($event, { type: 'folder', id: item.id })"
                @dragend="onDragEnd"
                @dragover="onDragOverFolder($event, item.id)"
                @dragleave="onDragLeaveFolder"
                @drop.prevent="onDropOnFolder(item.id)"
                @click="onDisplayItemClick($event, 'folder', item.id, i)"
                @dblclick="onFolderDblClick(item.data as FolderType)"
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
              <div v-else class="item"
                :class="{
                  dragging: dragItem?.type === 'note' && dragItem?.id === item.id,
                  selected: isSelected('note', item.id),
                }"
                draggable="true"
                @mousedown="onItemMouseDown('note', item.id)"
                @dragstart="onDragStart($event, { type: 'note', id: item.id })"
                @dragend="onDragEnd"
                @click="onDisplayItemClick($event, 'note', item.id, i)"
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

              <div class="insertion-line" :class="{ visible: insertionIndex === i + 1 }"
                @dragover.prevent="onDragOverGap($event, i + 1)" @drop.prevent="onDropReorder" />
            </template>

            <div v-if="displayItems.length === 0" class="empty">Ce dossier est vide</div>
          </template>
        </template>
      </div>
    </div>
  </div>

  <!-- Context menu -->
  <Teleport to="body">
    <div v-if="contextMenu" class="ctx-menu"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px' }"
      @click.stop
    >
      <!-- Multi-select menu -->
      <template v-if="contextMenu.kind === 'multiselect'">
        <button v-if="selectedNoteCount > 0" class="ctx-item" @click="copySelection">
          Copier ({{ selectedNoteCount }} note{{ selectedNoteCount > 1 ? 's' : '' }})
        </button>
        <div v-if="selectedNoteCount > 0" class="ctx-separator" />
        <button class="ctx-item danger" @click="ctxDeleteSelection">
          Supprimer ({{ selectedItems.size }})
        </button>
      </template>

      <!-- Note menu -->
      <template v-else-if="contextMenu.kind === 'note' && contextMenu.noteId !== undefined">
        <button v-if="contextMenu.inFavorites" class="ctx-item" @click="ctxRemoveFromFavorites(contextMenu.noteId)">Enlever des favoris</button>
        <div v-if="contextMenu.inFavorites" class="ctx-separator" />
        <button class="ctx-item" @click="startRenameNote(contextMenu.noteId)">Renommer</button>
        <button class="ctx-item" @click="copySingleNote(contextMenu.noteId)">Copier</button>
        <div class="ctx-separator" />
        <button class="ctx-item danger" @click="ctxDeleteNote(contextMenu.noteId)">Supprimer</button>
      </template>

      <!-- Folder menu -->
      <template v-else-if="contextMenu.kind === 'folder' && contextMenu.folderId !== undefined">
        <button class="ctx-item" @click="ctxCreateNoteInFolder(contextMenu.folderId)">Nouvelle note</button>
        <button class="ctx-item" @click="showNewFolder(contextMenu.folderId)">Nouveau sous-dossier</button>
        <div class="ctx-separator" />
        <button class="ctx-item" @click="startRenameFolder(contextMenu.folderId)">Renommer</button>
        <button class="ctx-item danger" @click="ctxDeleteFolder(contextMenu.folderId)">Supprimer</button>
      </template>

      <!-- Background menu -->
      <template v-else>
        <button class="ctx-item" @click="ctxCreateNoteHere">Nouvelle note</button>
        <button class="ctx-item" @click="showNewFolder(currentFolderId)">Nouveau dossier</button>
        <template v-if="canPaste">
          <div class="ctx-separator" />
          <button class="ctx-item" @click="pasteItems">
            Coller ({{ clipboard.length }} note{{ clipboard.length > 1 ? 's' : '' }})
          </button>
        </template>
      </template>
    </div>
  </Teleport>
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
  height: 560px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
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

.modal-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.selection-count {
  font-size: 11px;
  color: var(--color-accent-primary);
  margin-right: 6px;
}

.view-btn {
  background: transparent;
  border: 1px solid var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  padding: 4px 6px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: color 0.15s, border-color 0.15s;
}

.view-btn:hover { color: var(--color-text-primary); }
.view-btn.active { color: var(--color-accent-primary); border-color: var(--color-accent-primary); }

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
  padding: 2px 6px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color 0.15s, background-color 0.15s;
}

.breadcrumb-item:hover { color: var(--color-text-primary); background-color: var(--color-bg-tertiary); }
.breadcrumb-item.active { color: var(--color-text-primary); cursor: default; }
.breadcrumb-item.active:hover { background-color: transparent; }
.breadcrumb-item.drag-over {
  background-color: rgba(99, 179, 237, 0.15);
  color: var(--color-accent-primary);
  outline: 1px solid var(--color-accent-primary);
  outline-offset: -1px;
}

.breadcrumb-sep {
  color: var(--color-text-muted);
  font-size: 12px;
  padding: 0 2px;
  pointer-events: none;
}

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

/* List mode */
.modal-body.list .item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.1s;
  user-select: none;
}

.modal-body.list .item:hover { background-color: var(--color-bg-tertiary); }

/* Grid mode */
.modal-body.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(88px, 1fr));
  gap: 6px;
  align-content: start;
}

.modal-body.grid .item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 10px 6px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--color-bg-tertiary);
  text-align: center;
  transition: background-color 0.1s;
  user-select: none;
}

.modal-body.grid .item:hover { background-color: var(--color-bg-tertiary); }

.modal-body.grid .item-name {
  white-space: normal;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: break-word;
  font-size: 11px;
}

.modal-body.grid .insertion-line { display: none; }

/* Fallback (search results / favorites) */
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

.modal-body {
  position: relative;
}

.empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: 13px;
  pointer-events: none;
}

.breadcrumb-item > :deep(svg) {
  pointer-events: none;
}

.item.dragging { opacity: 0.4; }

.item.drag-over-folder {
  background-color: rgba(99, 179, 237, 0.12);
  outline: 1px solid var(--color-accent-primary);
  outline-offset: -1px;
}

.item.selected {
  background-color: rgba(99, 179, 237, 0.1);
  outline: 1px solid rgba(99, 179, 237, 0.35);
  outline-offset: -1px;
}

.item.selected:hover {
  background-color: rgba(99, 179, 237, 0.18);
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
</style>

<style>
.ctx-menu {
  position: fixed;
  z-index: 9999;
  background-color: #1e2a3a;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 4px;
  min-width: 180px;
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
</style>
