<script setup lang="ts">
import { FolderOpen, Star, PenLine } from "lucide-vue-next";

const emit = defineEmits<{
  (e: "open-modal"): void;
  (e: "open-favorites"): void;
  (e: "new-note"): void;
}>();
</script>

<template>
  <aside class="action-bar">
    <button class="action-btn" title="Fichiers" @click="emit('open-modal')">
      <FolderOpen :size="18" />
    </button>
    <button class="action-btn" title="Favoris" @click="emit('open-favorites')">
      <Star :size="18" />
    </button>
    <button class="action-btn" title="Nouvelle note" @click="emit('new-note')">
      <PenLine :size="18" />
    </button>
  </aside>
</template>

<style scoped>
.action-bar {
  width: 48px;
  background-color: var(--color-bg-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
  gap: 8px;
  flex-shrink: 0;
  border-right: 1px solid var(--color-bg-tertiary);
}

.action-btn {
  width: 36px;
  height: 36px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.action-btn:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}
</style>
