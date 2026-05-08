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
