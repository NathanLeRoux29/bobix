<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useNotesStore } from "../stores/notes";
import NotesTabs from "../components/notes/NotesTabs.vue";
import NotesEditor from "../components/notes/NotesEditor.vue";
import BobPanel from "../components/notes/BobPanel.vue";
import FilesModal from "../components/notes/FilesModal.vue";

const store = useNotesStore();
const isModalOpen = ref(false);
const modalFavoritesOnly = ref(false);

onMounted(async () => {
  await Promise.all([store.fetchNotes(), store.fetchFolders()]).catch(() => {});
});

function openModal(favoritesOnly = false) {
  modalFavoritesOnly.value = favoritesOnly;
  isModalOpen.value = true;
}
</script>

<template>
  <div class="notes-layout">
    <div class="notes-body">
      <div class="editor-col">
        <NotesTabs
          @open-modal="openModal(false)"
          @open-favorites="openModal(true)"
        />
        <NotesEditor v-if="store.activeTabId !== null" />
        <div v-else class="empty-state">
          <p>Ouvre une note depuis <strong>Fichiers</strong></p>
        </div>
      </div>
      <BobPanel v-if="store.isBobVisible" />
    </div>
  </div>

  <FilesModal
    v-if="isModalOpen"
    :favorites-only="modalFavoritesOnly"
    @close="isModalOpen = false"
  />
</template>

<style scoped>
.notes-layout {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.notes-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.editor-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: 14px;
}

.empty-state strong {
  color: var(--color-text-secondary);
}
</style>
