import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useNotesStore } from "../stores/notes";
import type { Note } from "../types/notes";

function mockNote(id: number): Note {
  return {
    id,
    title: `Note ${id}`,
    content: `Content ${id}`,
    folder_id: null,
    is_favorite: false,
    created_at: "2026-05-03T00:00:00Z",
    updated_at: "2026-05-03T00:00:00Z",
  };
}

describe("notes store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("has correct default state", () => {
    const store = useNotesStore();
    expect(store.openTabs).toEqual([]);
    expect(store.activeTabId).toBeNull();
    expect(store.isBobVisible).toBe(false);
    expect(store.pendingContent).toBe("");
    expect(store.pendingTitle).toBe("");
    expect(store.saveStatus).toBe("idle");
  });

  it("openNote — fetches and adds new tab", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(mockNote(1)) })
    );
    const store = useNotesStore();
    await store.openNote(1);
    expect(store.openTabs).toHaveLength(1);
    expect(store.activeTabId).toBe(1);
    expect(store.pendingContent).toBe("Content 1");
    expect(store.pendingTitle).toBe("Note 1");
  });

  it("openNote — already open: only sets active tab without fetching", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue({ ok: true, json: () => Promise.resolve(mockNote(1)) });
    vi.stubGlobal("fetch", fetchMock);
    const store = useNotesStore();
    await store.openNote(1);
    await store.openNote(1);
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(store.openTabs).toHaveLength(1);
  });

  it("closeTab — active tab activates the previous tab", async () => {
    let call = 0;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(mockNote(++call)) })
    );
    const store = useNotesStore();
    await store.openNote(1);
    await store.openNote(2);
    await store.closeTab(2);
    expect(store.activeTabId).toBe(1);
    expect(store.openTabs).toHaveLength(1);
  });

  it("closeTab — last tab clears activeTabId", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve(mockNote(1)) })
    );
    const store = useNotesStore();
    await store.openNote(1);
    await store.closeTab(1);
    expect(store.activeTabId).toBeNull();
    expect(store.openTabs).toHaveLength(0);
  });

  it("toggleBob — flips isBobVisible", () => {
    const store = useNotesStore();
    expect(store.isBobVisible).toBe(false);
    store.toggleBob();
    expect(store.isBobVisible).toBe(true);
    store.toggleBob();
    expect(store.isBobVisible).toBe(false);
  });

  it("toggleFavorite — sends PATCH with inverted is_favorite", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockNote(1)) })
      .mockResolvedValue({});
    vi.stubGlobal("fetch", fetchMock);
    const store = useNotesStore();
    await store.openNote(1);
    await store.toggleFavorite(1);
    expect(fetchMock).toHaveBeenLastCalledWith(
      "http://localhost:8000/api/notes/1",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ is_favorite: true }),
      })
    );
  });
});
