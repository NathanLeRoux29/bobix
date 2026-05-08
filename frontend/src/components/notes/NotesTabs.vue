<script setup lang="ts">
import { X, FolderOpen, PenLine, Star } from "lucide-vue-next";
import { useNotesStore } from "../../stores/notes";

const store = useNotesStore();

const emit = defineEmits<{
  (e: "open-modal"): void;
  (e: "open-favorites"): void;
}>();
</script>

<template>
  <div class="tabs-bar">
    <div class="tabs-actions">
      <button class="action-btn" @click="emit('open-modal')">
        <FolderOpen :size="14" /> Fichiers
      </button>
      <button class="action-btn" @click="store.createNote()">
        <PenLine :size="14" /> Nouvelle note
      </button>
      <button class="action-btn" @click="emit('open-favorites')">
        <Star :size="14" /> Ouvrir les favoris
      </button>
    </div>

    <div class="tabs-list">
      <button
        v-for="note in store.openTabs"
        :key="note.id"
        class="tab"
        :class="{ active: note.id === store.activeTabId }"
        @click="store.setActiveTab(note.id)"
      >
        <span class="tab-title">
          <span
            v-if="note.id === store.activeTabId && store.saveStatus === 'saving'"
            class="dot"
          >•</span>
          {{ note.title || "Sans titre" }}
        </span>
        <span
          v-if="note.id === store.activeTabId && store.saveStatus === 'error'"
          class="error-indicator"
        >⚠</span>
        <button class="tab-close" @click.stop="store.closeTab(note.id)">
          <X :size="11" />
        </button>
      </button>
    </div>
  </div>
</template>

<style scoped>
.tabs-bar {
  display: flex;
  align-items: stretch;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-bg-tertiary);
  flex-shrink: 0;
  min-height: 36px;
}

.tabs-actions {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 0 8px;
  border-right: 1px solid var(--color-bg-tertiary);
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.15s, color 0.15s;
}

.action-btn:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.tabs-list {
  display: flex;
  overflow-x: auto;
  flex: 1;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.12) transparent;
}

.tabs-list::-webkit-scrollbar { height: 5px; }
.tabs-list::-webkit-scrollbar-track { background: transparent; }
.tabs-list::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 3px; }

.tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-right: 1px solid var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: 13px;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.15s ease, color 0.15s ease;
  max-width: 180px;
}

.tab:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.tab.active {
  color: var(--color-accent-primary);
  background-color: var(--color-bg-primary);
  border-bottom: 2px solid var(--color-accent-primary);
}

.tab-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.dot {
  color: var(--color-warning);
}

.error-indicator {
  color: var(--color-error);
  font-size: 11px;
}

.tab-close {
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  cursor: pointer;
  padding: 2px;
  border-radius: 3px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-close:hover {
  color: var(--color-text-primary);
  background-color: var(--color-bg-tertiary);
}
</style>
