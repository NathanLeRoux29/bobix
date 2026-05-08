<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useSettingsStore } from "../stores/settings";
import { getGreetingMessage, getRandomTemplateId } from "../utils/greeting";

const router = useRouter();
const settings = useSettingsStore();

const ANIMATION_DURATION_MS = 3200;

onMounted(async () => {
  try {
    await settings.fetchSettings();
  } catch {
    // backend unavailable — keep defaults
  }
  if (!settings.greetingShow) {
    router.replace("/hub");
    return;
  }
  setTimeout(() => {
    router.replace("/hub");
  }, ANIMATION_DURATION_MS);
});

const message = computed(() => {
  const templateId = settings.greetingRandom
    ? getRandomTemplateId()
    : settings.greetingTemplate;
  return getGreetingMessage(templateId, settings.username, new Date().getHours());
});
</script>

<template>
  <div class="greeting-screen">
    <h1 class="greeting-message">{{ message }}</h1>
  </div>
</template>

<style scoped>
.greeting-screen {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: var(--color-bg-primary);
}

.greeting-message {
  font-size: 52px;
  font-weight: 300;
  color: var(--color-text-primary);
  text-align: center;
  letter-spacing: -0.5px;
  animation: fadeInOut 3.2s ease forwards;
}

@keyframes fadeInOut {
  0%   { opacity: 0; transform: translateY(10px); }
  20%  { opacity: 1; transform: translateY(0); }
  75%  { opacity: 1; transform: translateY(0); }
  100% { opacity: 0; transform: translateY(-6px); }
}
</style>
