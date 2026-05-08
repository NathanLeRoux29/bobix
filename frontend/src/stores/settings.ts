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
