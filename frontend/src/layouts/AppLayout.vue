<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="sidebar-logo">Bobix</div>
      <nav class="sidebar-nav">
        <RouterLink to="/hub" class="nav-item">Hub</RouterLink>
        <RouterLink to="/notes" class="nav-item">Notes</RouterLink>
        <RouterLink to="/tasks" class="nav-item">Tâches</RouterLink>
        <RouterLink to="/settings" class="nav-item">Paramètres</RouterLink>
      </nav>
    </aside>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background-color: var(--color-bg-primary);
}

.sidebar {
  width: 200px;
  background-color: var(--color-bg-secondary);
  display: flex;
  flex-direction: column;
  padding: 24px 0;
  flex-shrink: 0;
}

.sidebar-logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-accent-primary);
  padding: 0 20px 32px;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  padding: 10px 20px;
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: color 0.15s ease, background-color 0.15s ease;
}

.nav-item:hover {
  color: var(--color-text-primary);
  background-color: var(--color-bg-tertiary);
}

.nav-item.router-link-active {
  color: var(--color-accent-primary);
  background-color: var(--color-bg-tertiary);
}

.main-content {
  flex: 1;
  overflow: auto;
}
</style>
