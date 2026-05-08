import { defineStore } from "pinia";
import type { Note, Folder } from "../types/notes";

const API_BASE = "http://localhost:8000";

export type SaveStatus = "idle" | "saving" | "saved" | "error";

// Timer outside Pinia state to avoid serialization issues
let saveTimer: ReturnType<typeof setTimeout> | null = null;

export const useNotesStore = defineStore("notes", {
  state: () => ({
    openTabs: [] as Note[],
    activeTabId: null as number | null,
    isBobVisible: false,
    pendingContent: "",
    pendingTitle: "",
    saveStatus: "idle" as SaveStatus,
    allNotes: [] as Note[],
    folders: [] as Folder[],
  }),

  getters: {
    activeNote(state): Note | undefined {
      return state.openTabs.find((n) => n.id === state.activeTabId);
    },
  },

  actions: {
    async fetchNotes() {
      const res = await fetch(`${API_BASE}/api/notes/`);
      this.allNotes = await res.json();
    },

    async fetchFolders() {
      const res = await fetch(`${API_BASE}/api/folders/`);
      this.folders = await res.json();
    },

    async openNote(id: number) {
      const existing = this.openTabs.find((n) => n.id === id);
      if (existing) {
        this.setActiveTab(id);
        return;
      }
      const res = await fetch(`${API_BASE}/api/notes/${id}`);
      if (!res.ok) throw new Error("Note not found");
      const note: Note = await res.json();
      this.openTabs.push(note);
      this.setActiveTab(id);
    },

    setActiveTab(id: number) {
      this.activeTabId = id;
      const note = this.openTabs.find((n) => n.id === id);
      if (note) {
        this.pendingContent = note.content;
        this.pendingTitle = note.title;
        this.saveStatus = "idle";
      }
    },

    async closeTab(id: number) {
      if (saveTimer) {
        clearTimeout(saveTimer);
        saveTimer = null;
        if (this.activeTabId === id) await this.saveNote();
      }
      const idx = this.openTabs.findIndex((n) => n.id === id);
      this.openTabs.splice(idx, 1);
      if (this.activeTabId === id) {
        const next = this.openTabs[idx - 1] ?? this.openTabs[0];
        if (next) {
          this.setActiveTab(next.id);
        } else {
          this.activeTabId = null;
          this.pendingContent = "";
          this.pendingTitle = "";
          this.saveStatus = "idle";
        }
      }
    },

    scheduleSave() {
      if (saveTimer) clearTimeout(saveTimer);
      this.saveStatus = "saving";
      saveTimer = setTimeout(() => this.saveNote(), 1000);
    },

    async saveNote() {
      if (this.activeTabId === null) return;
      try {
        await fetch(`${API_BASE}/api/notes/${this.activeTabId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: this.pendingTitle,
            content: this.pendingContent,
          }),
        });
        const tab = this.openTabs.find((n) => n.id === this.activeTabId);
        if (tab) {
          tab.title = this.pendingTitle;
          tab.content = this.pendingContent;
        }
        this.saveStatus = "saved";
      } catch {
        this.saveStatus = "error";
        setTimeout(() => this.saveNote(), 3000);
      }
    },

    async toggleFavorite(id: number) {
      const inTabs = this.openTabs.find((n) => n.id === id);
      const inAll = this.allNotes.find((n) => n.id === id);
      const note = inTabs ?? inAll;
      if (!note) return;
      const newValue = !note.is_favorite;
      await fetch(`${API_BASE}/api/notes/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_favorite: newValue }),
      });
      if (inTabs) inTabs.is_favorite = newValue;
      if (inAll) inAll.is_favorite = newValue;
    },

    async createNote(folderId?: number) {
      const res = await fetch(`${API_BASE}/api/notes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: "Sans titre",
          content: "",
          folder_id: folderId ?? null,
        }),
      });
      const note: Note = await res.json();
      this.allNotes.push(note);
      this.openTabs.push(note);
      this.setActiveTab(note.id);
    },

    async renameNote(id: number, newTitle: string) {
      await fetch(`${API_BASE}/api/notes/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle }),
      });
      const inAll = this.allNotes.find((n) => n.id === id);
      if (inAll) inAll.title = newTitle;
      const inTab = this.openTabs.find((n) => n.id === id);
      if (inTab) {
        inTab.title = newTitle;
        if (this.activeTabId === id) this.pendingTitle = newTitle;
      }
    },

    async deleteNote(id: number) {
      await fetch(`${API_BASE}/api/notes/${id}`, { method: "DELETE" });
      this.allNotes = this.allNotes.filter((n) => n.id !== id);
      if (this.openTabs.find((n) => n.id === id)) {
        await this.closeTab(id);
      }
    },

    async createFolder(name: string, parentId?: number) {
      await fetch(`${API_BASE}/api/folders/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, parent_id: parentId ?? null }),
      });
      await this.fetchFolders();
    },

    async deleteFolder(id: number) {
      await fetch(`${API_BASE}/api/folders/${id}`, { method: "DELETE" });
      await this.fetchFolders();
    },

    async moveNote(noteId: number, folderId: number | null) {
      const note = this.allNotes.find((n) => n.id === noteId);
      if (!note) return;
      const prev = note.folder_id;
      note.folder_id = folderId;
      try {
        await fetch(`${API_BASE}/api/notes/${noteId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ folder_id: folderId }),
        });
      } catch {
        note.folder_id = prev;
      }
    },

    async moveFolder(folderId: number, parentId: number | null) {
      const folder = this.folders.find((f) => f.id === folderId);
      if (!folder) return;
      const prev = folder.parent_id;
      folder.parent_id = parentId;
      try {
        await fetch(`${API_BASE}/api/folders/${folderId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ parent_id: parentId }),
        });
      } catch {
        folder.parent_id = prev;
      }
    },

    async copyNote(sourceId: number, folderId: number | null, newTitle: string) {
      const source = this.allNotes.find((n) => n.id === sourceId);
      if (!source) return;
      const res = await fetch(`${API_BASE}/api/notes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: newTitle, content: source.content, folder_id: folderId }),
      });
      if (!res.ok) return;
      const note: Note = await res.json();
      this.allNotes.push(note);
    },

    async renameFolder(folderId: number, name: string) {
      const folder = this.folders.find((f) => f.id === folderId);
      if (!folder) return;
      const prev = folder.name;
      folder.name = name;
      try {
        await fetch(`${API_BASE}/api/folders/${folderId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name }),
        });
      } catch {
        folder.name = prev;
      }
    },

    toggleBob() {
      this.isBobVisible = !this.isBobVisible;
    },
  },
});
