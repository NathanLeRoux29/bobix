# Frontend Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Scaffold a Tauri 2.x + Vue 3 + TypeScript application with dark theme CSS variables, Vue Router, Pinia settings store, and a functional greeting screen backed by the existing FastAPI settings API.

**Architecture:** Single-page app living at the project root alongside `backend/`. Vue Router handles navigation between `/greeting` and `/hub`. Pinia reads/writes settings from the FastAPI backend. Greeting logic is in pure utility functions tested with Vitest (no DOM, no network). The CSS variable system is the single source of truth for all colors.

**Tech Stack:** Tauri 2.x, Vue 3, TypeScript, Vite, Vue Router 4, Pinia, Vitest, jsdom.

---

## File Map

**Create:**
- `index.html`
- `package.json`
- `tsconfig.json`
- `tsconfig.node.json`
- `vite.config.ts`
- `src/main.ts`
- `src/App.vue`
- `src/vite-env.d.ts`
- `src/assets/styles/default.css`
- `src/router/index.ts`
- `src/utils/greeting.ts`
- `src/stores/settings.ts`
- `src/views/GreetingView.vue`
- `src/views/HubView.vue`
- `src/__tests__/greeting.test.ts`
- `src/__tests__/settings.store.test.ts`
- `src-tauri/tauri.conf.json`
- `src-tauri/capabilities/default.json`
- `src-tauri/src/lib.rs`
- `src-tauri/src/main.rs`
- `src-tauri/build.rs`
- `src-tauri/Cargo.toml`
- `docs/dev/02-frontend.md`

---

## Task 1: Scaffold Tauri + Vue 3 + TypeScript at project root

**Files:**
- Create: `index.html`, `package.json`, `tsconfig.json`, `tsconfig.node.json`, `vite.config.ts`
- Create: `src/main.ts`, `src/App.vue`, `src/vite-env.d.ts`
- Create: `src-tauri/tauri.conf.json`, `src-tauri/capabilities/default.json`
- Create: `src-tauri/src/lib.rs`, `src-tauri/src/main.rs`, `src-tauri/build.rs`, `src-tauri/Cargo.toml`

- [ ] **Step 1: Run the Tauri scaffold in the project root**

```bash
# From the project root (/app)
npm create tauri-app@2 .
```

When prompted:
- Project name: `app`
- Frontend language: `TypeScript / JavaScript`
- Package manager: `npm`
- UI template: `Vue`
- UI flavor: `TypeScript`
- Identifier: `com.perso.app`

The scaffold creates `src/`, `src-tauri/`, `index.html`, `package.json`, `tsconfig.json`, `vite.config.ts`.

- [ ] **Step 2: Verify the scaffold succeeded**

```bash
ls
```

Expected output includes: `src/  src-tauri/  index.html  package.json  tsconfig.json  vite.config.ts  backend/  docs/`

- [ ] **Step 3: Install base dependencies**

```bash
npm install
```

Expected: installs vue, @tauri-apps/api, vite, etc. — no errors.

- [ ] **Step 4: Install additional dependencies**

```bash
npm install vue-router@4 pinia
npm install --save-dev vitest @vitest/coverage-v8 jsdom @vue/test-utils
```

- [ ] **Step 5: Add test script to `package.json`**

Open `package.json` and add to the `"scripts"` section:

```json
"test": "vitest run",
"test:watch": "vitest"
```

Final `"scripts"` section should look like:

```json
"scripts": {
  "dev": "vite",
  "build": "vue-tsc --noEmit && vite build",
  "tauri": "tauri",
  "test": "vitest run",
  "test:watch": "vitest"
}
```

- [ ] **Step 6: Commit**

```bash
git add index.html package.json package-lock.json tsconfig.json tsconfig.node.json vite.config.ts src/ src-tauri/
git commit -m "feat: scaffold Tauri 2 + Vue 3 + TypeScript frontend"
```

---

## Task 2: Configure Vitest in vite.config.ts

**Files:**
- Modify: `vite.config.ts`
- Modify: `tsconfig.json`

- [ ] **Step 1: Add Vitest config to `vite.config.ts`**

Replace the contents of `vite.config.ts` with:

```typescript
/// <reference types="vitest" />
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const host = process.env.TAURI_DEV_HOST;

export default defineConfig({
  plugins: [vue()],
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host
      ? { protocol: "ws", host, port: 1421 }
      : undefined,
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});
```

- [ ] **Step 2: Add Vitest types to `tsconfig.json`**

Open `tsconfig.json`. Add `"vitest/globals"` to the `"types"` array under `"compilerOptions"`. If the array doesn't exist, add it:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

If `tsconfig.json` already has a `"compilerOptions"` section, just add `"types": ["vitest/globals"]` to it.

- [ ] **Step 3: Verify Vitest runs (no tests yet — just check it doesn't crash)**

```bash
npm test
```

Expected: `No test files found` or exits 0. No import errors.

- [ ] **Step 4: Commit**

```bash
git add vite.config.ts tsconfig.json
git commit -m "chore: configure Vitest with jsdom environment"
```

---

## Task 3: CSS dark theme system

**Files:**
- Create: `src/assets/styles/default.css`
- Modify: `src/main.ts`

- [ ] **Step 1: Create `src/assets/styles/default.css`**

```css
/* CSS reset and dark theme default variables */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  /* Backgrounds */
  --color-bg-primary: #1a1a2e;
  --color-bg-secondary: #16213e;
  --color-bg-tertiary: #0f3460;

  /* Text */
  --color-text-primary: #eaeaea;
  --color-text-secondary: #a0a0a0;
  --color-text-muted: #6c6c6c;

  /* Accents */
  --color-accent-primary: #e94560;
  --color-accent-secondary: #533483;

  /* State colors */
  --color-success: #4ade80;
  --color-warning: #fbbf24;
  --color-error: #ef4444;

  /* Component-specific */
  --color-button-bg: #e94560;
  --color-button-text: #ffffff;
  --color-input-bg: #16213e;
  --color-input-border: #0f3460;
  --color-panel-ia-bg: #1a1a2e;
}

body {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-family: Inter, system-ui, -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
```

- [ ] **Step 2: Replace the default style import in `src/main.ts`**

Open `src/main.ts`. Remove any existing `import './styles.css'` line (or similar). The file currently looks like:

```typescript
import { createApp } from "vue";
import App from "./App.vue";

createApp(App).mount("#app");
```

Replace it with:

```typescript
import { createApp } from "vue";
import App from "./App.vue";
import "./assets/styles/default.css";

createApp(App).mount("#app");
```

(We'll add router and pinia in Task 4.)

- [ ] **Step 3: Delete the old styles file if it exists**

```bash
rm -f src/styles.css
```

- [ ] **Step 4: Commit**

```bash
git add src/assets/styles/default.css src/main.ts
git rm --cached src/styles.css 2>/dev/null || true
git commit -m "feat: add dark theme CSS variable system"
```

---

## Task 4: Vue Router — /greeting and /hub routes

**Files:**
- Create: `src/router/index.ts`
- Create: `src/views/GreetingView.vue` (stub — replaced in Task 7)
- Create: `src/views/HubView.vue` (stub — replaced in Task 8)
- Modify: `src/main.ts`
- Modify: `src/App.vue`

- [ ] **Step 1: Create `src/router/index.ts`**

```typescript
import { createRouter, createWebHistory } from "vue-router";
import GreetingView from "../views/GreetingView.vue";
import HubView from "../views/HubView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/greeting" },
    { path: "/greeting", component: GreetingView },
    { path: "/hub", component: HubView },
  ],
});
```

- [ ] **Step 2: Create stub `src/views/GreetingView.vue`**

```vue
<template>
  <div>Greeting — à venir</div>
</template>
```

- [ ] **Step 3: Create stub `src/views/HubView.vue`**

```vue
<template>
  <div>Hub — à venir</div>
</template>
```

- [ ] **Step 4: Wire router into `src/main.ts`**

```typescript
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./assets/styles/default.css";

createApp(App).use(createPinia()).use(router).mount("#app");
```

- [ ] **Step 5: Replace `src/App.vue` with a clean RouterView shell**

```vue
<template>
  <RouterView />
</template>
```

- [ ] **Step 6: Delete generated Tauri boilerplate components**

```bash
rm -f src/components/Greet.vue
rm -f src/assets/vue.svg
```

- [ ] **Step 7: Verify the dev server starts**

```bash
npm run dev
```

Expected: Vite starts on `http://localhost:1420`. No TypeScript errors.
Open `http://localhost:1420` in a browser — you should be redirected to `/greeting` and see "Greeting — à venir".

- [ ] **Step 8: Commit**

```bash
git add src/router/index.ts src/views/ src/main.ts src/App.vue
git rm --cached src/components/Greet.vue src/assets/vue.svg 2>/dev/null || true
git commit -m "feat: add Vue Router with /greeting and /hub routes"
```

---

## Task 5: Greeting utility — pure functions (TDD)

**Files:**
- Create: `src/__tests__/greeting.test.ts`
- Create: `src/utils/greeting.ts`

- [ ] **Step 1: Write the failing tests in `src/__tests__/greeting.test.ts`**

```typescript
import { describe, it, expect } from "vitest";
import {
  getTimeOfDay,
  getGreetingMessage,
  getRandomTemplateId,
  TEMPLATE_IDS,
} from "../utils/greeting";

describe("getTimeOfDay", () => {
  it("returns matinée for hours 5 to 11", () => {
    expect(getTimeOfDay(5)).toBe("matinée");
    expect(getTimeOfDay(9)).toBe("matinée");
    expect(getTimeOfDay(11)).toBe("matinée");
  });

  it("returns après-midi for hours 12 to 17", () => {
    expect(getTimeOfDay(12)).toBe("après-midi");
    expect(getTimeOfDay(15)).toBe("après-midi");
    expect(getTimeOfDay(17)).toBe("après-midi");
  });

  it("returns soirée for hours 18 to 23 and 0 to 4", () => {
    expect(getTimeOfDay(18)).toBe("soirée");
    expect(getTimeOfDay(23)).toBe("soirée");
    expect(getTimeOfDay(0)).toBe("soirée");
    expect(getTimeOfDay(4)).toBe("soirée");
  });
});

describe("getGreetingMessage", () => {
  it("formats salut template", () => {
    expect(getGreetingMessage("salut", "Marc", 9)).toBe("Salut Marc !");
  });

  it("formats bienvenue template", () => {
    expect(getGreetingMessage("bienvenue", "Marc", 9)).toBe("Bienvenue Marc");
  });

  it("formats pret template", () => {
    expect(getGreetingMessage("pret", "Marc", 9)).toBe(
      "Marc, prêt à travailler ?"
    );
  });

  it("formats hello template with emoji", () => {
    expect(getGreetingMessage("hello", "Marc", 9)).toBe("Hello Marc 👋");
  });

  it("formats bonjour template with matinée", () => {
    expect(getGreetingMessage("bonjour", "Marc", 9)).toBe(
      "Bonjour Marc, bonne matinée"
    );
  });

  it("formats bonjour template with après-midi", () => {
    expect(getGreetingMessage("bonjour", "Marc", 14)).toBe(
      "Bonjour Marc, bonne après-midi"
    );
  });

  it("formats bonjour template with soirée", () => {
    expect(getGreetingMessage("bonjour", "Marc", 20)).toBe(
      "Bonjour Marc, bonne soirée"
    );
  });
});

describe("getRandomTemplateId", () => {
  it("returns a valid template ID", () => {
    const id = getRandomTemplateId();
    expect(TEMPLATE_IDS).toContain(id);
  });

  it("returns different values over multiple calls (probabilistic)", () => {
    const results = new Set(Array.from({ length: 50 }, getRandomTemplateId));
    expect(results.size).toBeGreaterThan(1);
  });
});
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
npm test
```

Expected: FAIL — `Cannot find module '../utils/greeting'`

- [ ] **Step 3: Implement `src/utils/greeting.ts`**

```typescript
export type TimeOfDay = "matinée" | "après-midi" | "soirée";

export type GreetingTemplateId =
  | "salut"
  | "bienvenue"
  | "pret"
  | "hello"
  | "bonjour";

export const TEMPLATE_IDS: GreetingTemplateId[] = [
  "salut",
  "bienvenue",
  "pret",
  "hello",
  "bonjour",
];

export function getTimeOfDay(hour: number): TimeOfDay {
  if (hour >= 5 && hour < 12) return "matinée";
  if (hour >= 12 && hour < 18) return "après-midi";
  return "soirée";
}

export function getGreetingMessage(
  templateId: GreetingTemplateId,
  username: string,
  hour: number
): string {
  const moment = getTimeOfDay(hour);
  const templates: Record<GreetingTemplateId, string> = {
    salut: `Salut ${username} !`,
    bienvenue: `Bienvenue ${username}`,
    pret: `${username}, prêt à travailler ?`,
    hello: `Hello ${username} 👋`,
    bonjour: `Bonjour ${username}, bonne ${moment}`,
  };
  return templates[templateId];
}

export function getRandomTemplateId(): GreetingTemplateId {
  return TEMPLATE_IDS[Math.floor(Math.random() * TEMPLATE_IDS.length)];
}
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
npm test
```

Expected: 10 tests pass, 0 failures.

- [ ] **Step 5: Commit**

```bash
git add src/__tests__/greeting.test.ts src/utils/greeting.ts
git commit -m "feat: add greeting utility with getTimeOfDay and getGreetingMessage"
```

---

## Task 6: Pinia settings store (TDD)

**Files:**
- Create: `src/__tests__/settings.store.test.ts`
- Create: `src/stores/settings.ts`

- [ ] **Step 1: Write the failing tests in `src/__tests__/settings.store.test.ts`**

```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useSettingsStore } from "../stores/settings";

describe("settings store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("has correct default state", () => {
    const store = useSettingsStore();
    expect(store.username).toBe("Utilisateur");
    expect(store.greetingTemplate).toBe("salut");
    expect(store.greetingRandom).toBe(false);
    expect(store.greetingShow).toBe(true);
  });

  it("fetchSettings populates state from API response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: () =>
          Promise.resolve([
            { key: "username", value: "Marc" },
            { key: "greeting_template", value: "bonjour" },
            { key: "greeting_random", value: "true" },
            { key: "greeting_show", value: "false" },
          ]),
      })
    );

    const store = useSettingsStore();
    await store.fetchSettings();

    expect(store.username).toBe("Marc");
    expect(store.greetingTemplate).toBe("bonjour");
    expect(store.greetingRandom).toBe(true);
    expect(store.greetingShow).toBe(false);

    vi.unstubAllGlobals();
  });

  it("fetchSettings ignores unknown keys", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        json: () =>
          Promise.resolve([{ key: "unknown_key", value: "something" }]),
      })
    );

    const store = useSettingsStore();
    await store.fetchSettings();

    // Defaults unchanged
    expect(store.username).toBe("Utilisateur");
    vi.unstubAllGlobals();
  });

  it("updateSetting calls PUT /api/settings/{key}", async () => {
    const mockFetch = vi.fn().mockResolvedValue({});
    vi.stubGlobal("fetch", mockFetch);

    const store = useSettingsStore();
    await store.updateSetting("username", "Alice");

    expect(mockFetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/settings/username",
      expect.objectContaining({
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value: "Alice" }),
      })
    );

    vi.unstubAllGlobals();
  });
});
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
npm test
```

Expected: FAIL — `Cannot find module '../stores/settings'`

- [ ] **Step 3: Implement `src/stores/settings.ts`**

```typescript
import { defineStore } from "pinia";
import type { GreetingTemplateId } from "../utils/greeting";

const API_BASE = "http://localhost:8000";

interface SettingsState {
  username: string;
  greetingTemplate: GreetingTemplateId;
  greetingRandom: boolean;
  greetingShow: boolean;
}

export const useSettingsStore = defineStore("settings", {
  state: (): SettingsState => ({
    username: "Utilisateur",
    greetingTemplate: "salut",
    greetingRandom: false,
    greetingShow: true,
  }),

  actions: {
    async fetchSettings() {
      const res = await fetch(`${API_BASE}/api/settings/`);
      const items: Array<{ key: string; value: string }> = await res.json();
      for (const item of items) {
        if (item.key === "username") this.username = item.value;
        if (item.key === "greeting_template")
          this.greetingTemplate = item.value as GreetingTemplateId;
        if (item.key === "greeting_random")
          this.greetingRandom = item.value === "true";
        if (item.key === "greeting_show")
          this.greetingShow = item.value === "true";
      }
    },

    async updateSetting(key: string, value: string) {
      await fetch(`${API_BASE}/api/settings/${key}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value }),
      });
    },
  },
});
```

- [ ] **Step 4: Run all tests to confirm they all pass**

```bash
npm test
```

Expected: 14 tests pass (10 greeting + 4 settings store), 0 failures.

- [ ] **Step 5: Commit**

```bash
git add src/__tests__/settings.store.test.ts src/stores/settings.ts
git commit -m "feat: add Pinia settings store with fetchSettings and updateSetting"
```

---

## Task 7: GreetingView component

**Files:**
- Modify: `src/views/GreetingView.vue` (replace stub from Task 4)

- [ ] **Step 1: Replace the stub with the full GreetingView**

```vue
<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useSettingsStore } from "../stores/settings";
import { getGreetingMessage, getRandomTemplateId } from "../utils/greeting";

const router = useRouter();
const settings = useSettingsStore();

onMounted(async () => {
  await settings.fetchSettings();
  if (!settings.greetingShow) {
    router.replace("/hub");
  }
});

const message = computed(() => {
  const templateId = settings.greetingRandom
    ? getRandomTemplateId()
    : settings.greetingTemplate;
  return getGreetingMessage(templateId, settings.username, new Date().getHours());
});

function continuer() {
  router.push("/hub");
}
</script>

<template>
  <div class="greeting-screen" @click="continuer">
    <div class="greeting-content">
      <hr class="divider" />
      <h1 class="greeting-message">{{ message }}</h1>
      <hr class="divider" />
      <button class="continuer-btn" @click.stop="continuer">Continuer →</button>
    </div>
  </div>
</template>

<style scoped>
.greeting-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: var(--color-bg-primary);
  cursor: pointer;
  user-select: none;
}

.greeting-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.divider {
  width: 240px;
  border: none;
  border-top: 1px solid var(--color-bg-tertiary);
}

.greeting-message {
  font-size: 52px;
  font-weight: 300;
  color: var(--color-text-primary);
  text-align: center;
  letter-spacing: -0.5px;
}

.continuer-btn {
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  padding: 8px 16px;
  transition: color 0.15s ease;
}

.continuer-btn:hover {
  color: var(--color-text-primary);
}
</style>
```

- [ ] **Step 2: Verify the greeting screen works**

Make sure the backend is running (`docker compose up -d`), then start the frontend:

```bash
npm run dev
```

Open `http://localhost:1420`. You should see:
- Dark background (`#1a1a2e`)
- A greeting message like "Salut Utilisateur !" centered in large type
- Horizontal dividers above and below the message
- "Continuer →" button at the bottom
- Clicking anywhere (or the button) redirects to `/hub`

If the backend is not running, the greeting screen should still display the fallback defaults (`username: "Utilisateur"`, `greetingTemplate: "salut"`).

- [ ] **Step 3: Commit**

```bash
git add src/views/GreetingView.vue
git commit -m "feat: implement GreetingView with settings store and time-aware templates"
```

---

## Task 8: HubView placeholder + App.vue cleanup

**Files:**
- Modify: `src/views/HubView.vue` (replace stub from Task 4)

- [ ] **Step 1: Replace the HubView stub with a styled placeholder**

```vue
<script setup lang="ts">
</script>

<template>
  <div class="hub-screen">
    <h1 class="hub-title">Hub</h1>
    <p class="hub-subtitle">À venir — Plan 3</p>
  </div>
</template>

<style scoped>
.hub-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: var(--color-bg-primary);
  gap: 12px;
}

.hub-title {
  font-size: 32px;
  font-weight: 300;
  color: var(--color-text-primary);
}

.hub-subtitle {
  font-size: 14px;
  color: var(--color-text-muted);
}
</style>
```

- [ ] **Step 2: Verify the full flow end-to-end**

```bash
npm run dev
```

Steps to test:
1. Open `http://localhost:1420` — redirects to `/greeting`, shows greeting message
2. Click "Continuer →" or click anywhere — navigates to `/hub`, shows "Hub / À venir"
3. Open browser DevTools → Network → verify `GET http://localhost:8000/api/settings/` is called (if backend is running)

- [ ] **Step 3: Commit**

```bash
git add src/views/HubView.vue
git commit -m "feat: add HubView placeholder with dark theme styling"
```

---

## Task 9: Documentation

**Files:**
- Create: `docs/dev/02-frontend.md`

- [ ] **Step 1: Create `docs/dev/02-frontend.md`**

```markdown
# 02 — Frontend : Tauri + Vue 3

**Plan :** [2026-05-01-frontend-base.md](../superpowers/plans/2026-05-01-frontend-base.md)
**Statut :** ✅ Terminé — 14 tests passent

---

## Contexte

Le frontend est une application desktop Tauri 2.x intégrant Vue 3 + TypeScript. Il consomme l'API FastAPI via `fetch` HTTP standard. Le frontend ne se connecte jamais directement à la base de données — tout passe par `http://localhost:8000`.

---

## Architecture

```
Tauri WebView
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
src/
├── main.ts                       # Point d'entrée Vue
├── App.vue                       # Shell : <RouterView />
├── vite-env.d.ts                 # Types Vite
│
├── assets/
│   └── styles/
│       └── default.css           # Variables CSS (thème sombre)
│
├── router/
│   └── index.ts                  # Routes: /, /greeting, /hub
│
├── stores/
│   └── settings.ts               # Pinia: username, greeting prefs
│
├── utils/
│   └── greeting.ts               # getTimeOfDay, getGreetingMessage
│
├── views/
│   ├── GreetingView.vue          # Écran de salutation
│   └── HubView.vue               # Hub (placeholder Plan 2)
│
└── __tests__/
    ├── greeting.test.ts          # Tests utils (10 tests)
    └── settings.store.test.ts    # Tests store (4 tests)
```

---

## Composants principaux

### `src/utils/greeting.ts`

Fonctions pures sans effet de bord. Aucune dépendance externe.

| Fonction | Description |
|----------|-------------|
| `getTimeOfDay(hour)` | Retourne `'matinée'` (5-11h), `'après-midi'` (12-17h) ou `'soirée'` (18-4h) |
| `getGreetingMessage(templateId, username, hour)` | Génère le message selon le template |
| `getRandomTemplateId()` | Retourne un templateId aléatoire parmi les 5 |

Templates disponibles : `salut`, `bienvenue`, `pret`, `hello`, `bonjour`

### `src/stores/settings.ts`

Store Pinia qui lit et écrit les préférences utilisateur dans le backend.

| État | Type | Défaut |
|------|------|--------|
| `username` | string | `'Utilisateur'` |
| `greetingTemplate` | GreetingTemplateId | `'salut'` |
| `greetingRandom` | boolean | `false` |
| `greetingShow` | boolean | `true` |

Actions : `fetchSettings()` → `GET /api/settings/` | `updateSetting(key, value)` → `PUT /api/settings/{key}`

### `src/views/GreetingView.vue`

Écran plein écran affiché au démarrage. Lance `fetchSettings()` au montage. Si `greetingShow = false`, redirige immédiatement vers `/hub`. Si `greetingRandom = true`, choisit un template au hasard.

### `src/assets/styles/default.css`

Source unique de vérité pour toutes les couleurs. Chaque composant utilise les variables CSS — jamais de couleurs codées en dur.

Variables principales :
- `--color-bg-primary: #1a1a2e` — fond général
- `--color-accent-primary: #e94560` — rouge accent
- `--color-text-primary: #eaeaea` — texte principal

---

## Lancer en local

```bash
# Frontend uniquement (hot reload, pas de Tauri)
npm run dev
# → http://localhost:1420

# Avec Tauri (application desktop)
npm run tauri dev

# Tests unitaires
npm test
# → 14 tests, 0 échec
```

---

## Tests

**14 tests — 0 échec.** Aucun backend requis (fonctions pures + mock fetch).

```bash
npm test
```

| Suite | Fichier | Tests |
|-------|---------|-------|
| Utils — Greeting | `src/__tests__/greeting.test.ts` | 10 |
| Store — Settings | `src/__tests__/settings.store.test.ts` | 4 |

**Architecture de test :**
- Les tests de `greeting.ts` sont purement unitaires — pas de DOM, pas de réseau.
- Les tests du store utilisent `vi.stubGlobal('fetch', ...)` pour simuler les réponses API sans démarrer le backend.
- `setActivePinia(createPinia())` dans `beforeEach` isole chaque test avec un store frais.

---

## Liens

- [→ Référence API](./api-reference.md)
- [→ Plan d'implémentation](../superpowers/plans/2026-05-01-frontend-base.md)
- [→ Spécifications générales](../specs/2026-05-01-app-design.md)
```

- [ ] **Step 2: Commit**

```bash
git add docs/dev/02-frontend.md
git commit -m "docs: add Plan 2 frontend onboarding doc"
```

---

## Self-review

**Spec coverage check:**

| Spec requirement | Task |
|-----------------|------|
| Tauri 2.x + Vue 3 + TypeScript + Vite | Task 1 |
| Pinia (stores) | Task 1 + Task 6 |
| Vue Router (routes) | Task 4 |
| CSS variables dark theme (`#1a1a2e`, `#e94560`, etc.) | Task 3 |
| 5 greeting templates (salut, bienvenue, pret, hello, bonjour) | Task 5 |
| `{moment}` time detection (matinée/après-midi/soirée) | Task 5 |
| Random template option | Task 5 + Task 7 |
| `greetingShow` toggle (auto-skip to hub) | Task 7 |
| Settings backed by backend `/api/settings/` | Task 6 |
| "Continuer →" button | Task 7 |
| Full-screen greeting layout (48px+ text, centered) | Task 7 |
| HubView placeholder | Task 8 |
| Vitest unit tests | Tasks 5, 6 |
| Documentation | Task 9 |

**Placeholder scan:** No TBDs, no "implement later", all code blocks are complete.

**Type consistency:** `GreetingTemplateId` defined in `greeting.ts`, imported in `settings.ts` and `GreetingView.vue`. `TEMPLATE_IDS` used in both `getRandomTemplateId` and the test assertion. All consistent.
