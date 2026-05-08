<template>
  <aside class="bob-panel">
    <div class="bob-header">
      <span class="bob-title">Bob</span>
    </div>
    <div class="bob-content">
      <p class="bob-placeholder">À venir — Plan 6</p>
    </div>
  </aside>
</template>

<style scoped>
.bob-panel {
  width: 300px;
  background-color: var(--color-bg-secondary);
  border-left: 1px solid var(--color-bg-tertiary);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.bob-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-bg-tertiary);
}

.bob-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-accent-primary);
}

.bob-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bob-placeholder {
  font-size: 13px;
  color: var(--color-text-muted);
}
</style>
