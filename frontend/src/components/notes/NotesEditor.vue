<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from "vue";
import { useEditor, EditorContent } from "@tiptap/vue-3";
import StarterKit from "@tiptap/starter-kit";
import { Color } from "@tiptap/extension-color";
import { TextStyle } from "@tiptap/extension-text-style";
import Highlight from "@tiptap/extension-highlight";
import { Markdown } from "tiptap-markdown";
import {
  Star, Bot, Palette,
  Bold, Italic, Strikethrough, Code, Terminal, Quote,
  List, ListOrdered, Minus, Heading1, Heading2, Heading3,
} from "lucide-vue-next";
import { useNotesStore } from "../../stores/notes";

const store = useNotesStore();

const editor = useEditor({
  extensions: [
    StarterKit,
    TextStyle,
    Color,
    Highlight.configure({ multicolor: true }),
    Markdown.configure({ html: false, transformPastedText: true }),
  ],
  content: store.pendingContent,
  editorProps: {
    attributes: { class: "editor-textarea" },
  },
  onUpdate({ editor }) {
    const storage = editor.storage as Record<string, any>;
    store.pendingContent = storage.markdown?.getMarkdown() ?? editor.getText();
    store.scheduleSave();
  },
});

// Sync content when active note changes
watch(
  () => store.activeTabId,
  () => {
    if (!editor.value) return;
    const storage = editor.value.storage as Record<string, any>;
    const current = storage.markdown?.getMarkdown() ?? editor.value.getText();
    if (current !== store.pendingContent) {
      editor.value.commands.setContent(store.pendingContent);
    }
  }
);

function onTitleInput(e: Event) {
  store.pendingTitle = (e.target as HTMLInputElement).value;
  store.scheduleSave();
}

// Toolbar helpers
function cmd(fn: () => void) {
  return () => { fn(); editor.value?.commands.focus(); };
}

const actions = {
  h1:           cmd(() => editor.value?.chain().focus().toggleHeading({ level: 1 }).run()),
  h2:           cmd(() => editor.value?.chain().focus().toggleHeading({ level: 2 }).run()),
  h3:           cmd(() => editor.value?.chain().focus().toggleHeading({ level: 3 }).run()),
  bold:         cmd(() => editor.value?.chain().focus().toggleBold().run()),
  italic:       cmd(() => editor.value?.chain().focus().toggleItalic().run()),
  strike:       cmd(() => editor.value?.chain().focus().toggleStrike().run()),
  code:         cmd(() => editor.value?.chain().focus().toggleCode().run()),
  codeBlock:    cmd(() => editor.value?.chain().focus().toggleCodeBlock().run()),
  blockquote:   cmd(() => editor.value?.chain().focus().toggleBlockquote().run()),
  bulletList:   cmd(() => editor.value?.chain().focus().toggleBulletList().run()),
  orderedList:  cmd(() => editor.value?.chain().focus().toggleOrderedList().run()),
  hr:           cmd(() => editor.value?.chain().focus().setHorizontalRule().run()),
};

function isActive(name: string, attrs?: Record<string, unknown>) {
  return editor.value?.isActive(name, attrs) ?? false;
}

// Color palette
const showColorPicker = ref(false);

const TEXT_COLORS = [
  { label: "Défaut",  value: null },
  { label: "Rouge",   value: "#ef4444" },
  { label: "Orange",  value: "#f97316" },
  { label: "Jaune",   value: "#eab308" },
  { label: "Vert",    value: "#22c55e" },
  { label: "Cyan",    value: "#06b6d4" },
  { label: "Bleu",    value: "#3b82f6" },
  { label: "Violet",  value: "#a855f7" },
  { label: "Rose",    value: "#ec4899" },
  { label: "Gris",    value: "#9ca3af" },
];

const HIGHLIGHT_COLORS = [
  { label: "Aucun",   value: null },
  { label: "Rouge",   value: "#fca5a5" },
  { label: "Orange",  value: "#fdba74" },
  { label: "Jaune",   value: "#fde047" },
  { label: "Vert",    value: "#86efac" },
  { label: "Cyan",    value: "#67e8f9" },
  { label: "Bleu",    value: "#93c5fd" },
  { label: "Violet",  value: "#d8b4fe" },
  { label: "Rose",    value: "#f9a8d4" },
];

function applyTextColor(color: string | null) {
  if (color === null) {
    editor.value?.chain().focus().unsetColor().run();
  } else {
    editor.value?.chain().focus().setColor(color).run();
  }
  showColorPicker.value = false;
}

function applyHighlight(color: string | null) {
  if (color === null) {
    editor.value?.chain().focus().unsetHighlight().run();
  } else {
    editor.value?.chain().focus().setHighlight({ color }).run();
  }
  showColorPicker.value = false;
}

function closeColorPicker() { showColorPicker.value = false; }
onMounted(() => document.addEventListener("click", closeColorPicker));
onUnmounted(() => document.removeEventListener("click", closeColorPicker));

function currentTextColor(): string {
  const attrs = editor.value?.getAttributes("textStyle") as { color?: string } | undefined;
  return attrs?.color ?? "#ffffff";
}
</script>

<template>
  <div class="editor">
    <div class="editor-toolbar">
      <!-- Left: title -->
      <div class="toolbar-left">
        <input
          class="title-input"
          :value="store.pendingTitle"
          placeholder="Sans titre"
          @input="onTitleInput"
        />
      </div>

      <!-- Center: format buttons -->
      <div class="format-bar">
        <div class="fmt-group">
          <button class="fmt-btn" :class="{ active: isActive('heading', { level: 1 }) }" title="Titre 1" @mousedown.prevent="actions.h1()"><Heading1 :size="15" /></button>
          <button class="fmt-btn" :class="{ active: isActive('heading', { level: 2 }) }" title="Titre 2" @mousedown.prevent="actions.h2()"><Heading2 :size="15" /></button>
          <button class="fmt-btn" :class="{ active: isActive('heading', { level: 3 }) }" title="Titre 3" @mousedown.prevent="actions.h3()"><Heading3 :size="15" /></button>
        </div>
        <div class="fmt-sep" />
        <div class="fmt-group">
          <button class="fmt-btn" :class="{ active: isActive('bold') }" title="Gras" @mousedown.prevent="actions.bold()"><Bold :size="15" /></button>
          <button class="fmt-btn" :class="{ active: isActive('italic') }" title="Italique" @mousedown.prevent="actions.italic()"><Italic :size="15" /></button>
          <button class="fmt-btn" :class="{ active: isActive('strike') }" title="Barré" @mousedown.prevent="actions.strike()"><Strikethrough :size="15" /></button>
        </div>
        <div class="fmt-sep" />
        <div class="fmt-group">
          <button class="fmt-btn" :class="{ active: isActive('code') }" title="Code inline" @mousedown.prevent="actions.code()"><Code :size="15" /></button>
          <button class="fmt-btn" :class="{ active: isActive('codeBlock') }" title="Bloc de code" @mousedown.prevent="actions.codeBlock()"><Terminal :size="15" /></button>
        </div>
        <div class="fmt-sep" />
        <div class="fmt-group">
          <button class="fmt-btn" :class="{ active: isActive('blockquote') }" title="Citation" @mousedown.prevent="actions.blockquote()"><Quote :size="15" /></button>
          <button class="fmt-btn" :class="{ active: isActive('bulletList') }" title="Liste à puces" @mousedown.prevent="actions.bulletList()"><List :size="15" /></button>
          <button class="fmt-btn" :class="{ active: isActive('orderedList') }" title="Liste numérotée" @mousedown.prevent="actions.orderedList()"><ListOrdered :size="15" /></button>
          <button class="fmt-btn" title="Séparateur" @mousedown.prevent="actions.hr()"><Minus :size="15" /></button>
        </div>
        <div class="fmt-sep" />
        <!-- Color picker -->
        <div class="color-picker-wrap" @click.stop>
          <button
            class="fmt-btn color-btn"
            title="Couleur"
            @mousedown.prevent="showColorPicker = !showColorPicker"
          >
            <Palette :size="15" />
            <span class="color-bar" :style="{ background: currentTextColor() }" />
          </button>
          <div v-if="showColorPicker" class="color-dropdown" @mousedown.prevent>
            <div class="color-section-label">Texte</div>
            <div class="color-swatches">
              <button
                v-for="c in TEXT_COLORS"
                :key="c.label"
                class="swatch"
                :class="{ 'swatch-default': c.value === null }"
                :style="c.value ? { background: c.value } : {}"
                :title="c.label"
                @click="applyTextColor(c.value)"
              />
            </div>
            <div class="color-section-label">Surlignage</div>
            <div class="color-swatches">
              <button
                v-for="c in HIGHLIGHT_COLORS"
                :key="c.label"
                class="swatch"
                :class="{ 'swatch-default': c.value === null }"
                :style="c.value ? { background: c.value } : {}"
                :title="c.label"
                @click="applyHighlight(c.value)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Right: actions -->
      <div class="toolbar-right">
        <button
          class="icon-btn"
          :class="{ active: store.activeNote?.is_favorite }"
          @click="store.toggleFavorite(store.activeTabId!)"
        >
          <Star :size="15" :fill="store.activeNote?.is_favorite ? 'currentColor' : 'none'" />
        </button>
        <button class="icon-btn" :class="{ active: store.isBobVisible }" @click="store.toggleBob()">
          <Bot :size="15" /> Bob
        </button>
      </div>
    </div>

    <div class="editor-body">
      <div class="editor-doc">
        <EditorContent :editor="editor" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-toolbar {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  background-color: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-bg-tertiary);
  flex-shrink: 0;
}

.toolbar-left { min-width: 0; }

.title-input {
  width: 100%;
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: 16px;
  font-weight: 500;
  outline: none;
}

.title-input::placeholder { color: var(--color-text-muted); }

.format-bar {
  display: flex;
  align-items: center;
  gap: 2px;
}

.fmt-group {
  display: flex;
  align-items: center;
  gap: 1px;
}

.fmt-sep {
  width: 1px;
  height: 18px;
  background-color: var(--color-bg-tertiary);
  margin: 0 5px;
}

.fmt-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text-muted);
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: color 0.12s, background-color 0.12s;
}

.fmt-btn:hover { color: var(--color-text-primary); background-color: var(--color-bg-tertiary); }
.fmt-btn.active { color: var(--color-accent-primary); }

.color-picker-wrap {
  position: relative;
}

.color-btn {
  flex-direction: column;
  gap: 2px;
  padding: 4px 8px;
}

.color-bar {
  width: 15px;
  height: 3px;
  border-radius: 2px;
}

.color-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-bg-tertiary);
  border-radius: 8px;
  padding: 10px 12px;
  z-index: 50;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  min-width: 180px;
}

.color-section-label {
  font-size: 11px;
  color: var(--color-text-muted);
  margin-bottom: 6px;
  margin-top: 4px;
}

.color-section-label:first-child { margin-top: 0; }

.color-swatches {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.swatch {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.15);
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.1s;
}

.swatch:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 2px var(--color-accent-primary);
}

.swatch-default {
  background: linear-gradient(135deg, #fff 40%, #f00 40%, #f00 60%, #fff 60%);
  background-size: 100% 100%;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
}

.icon-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  border: 1px solid var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: color 0.15s, background-color 0.15s, border-color 0.15s;
}

.icon-btn:hover { color: var(--color-text-primary); background-color: var(--color-bg-tertiary); }
.icon-btn.active { color: var(--color-accent-primary); border-color: var(--color-accent-primary); }

.editor-body {
  flex: 1;
  overflow-y: auto;
  background-color: var(--color-bg-primary);
  padding: 32px 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.12) transparent;
}

.editor-body::-webkit-scrollbar { width: 6px; }
.editor-body::-webkit-scrollbar-track { background: transparent; }
.editor-body::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 3px; }
.editor-body::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.25); }

.editor-doc {
  width: 100%;
  max-width: 860px;
  background-color: var(--color-bg-secondary);
  border-radius: 4px;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.5);
  min-height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
}
</style>

<style>
/* TipTap editor content — not scoped so it applies inside EditorContent */
.editor-textarea {
  width: 100%;
  min-height: calc(100vh - 120px);
  padding: 40px 52px;
  color: var(--color-text-primary);
  font-size: 14px;
  line-height: 1.7;
  outline: none;
  box-sizing: border-box;
}

.editor-textarea p { margin: 0 0 0.5em; }
.editor-textarea p:last-child { margin-bottom: 0; }

.editor-textarea h1,
.editor-textarea h2,
.editor-textarea h3 {
  color: var(--color-text-primary);
  margin: 1em 0 0.4em;
  line-height: 1.3;
}

.editor-textarea h1 { font-size: 2em; }
.editor-textarea h2 { font-size: 1.5em; }
.editor-textarea h3 { font-size: 1.2em; }

.editor-textarea strong { font-weight: 700; }
.editor-textarea em { font-style: italic; }
.editor-textarea s { text-decoration: line-through; }

.editor-textarea code {
  background-color: var(--color-bg-primary);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: "Fira Code", "Cascadia Code", monospace;
  font-size: 13px;
  color: var(--color-text-primary);
}

.editor-textarea pre {
  background-color: var(--color-bg-primary);
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 1em 0;
}

.editor-textarea pre code {
  background: none;
  padding: 0;
  font-size: 13px;
}

.editor-textarea blockquote {
  border-left: 3px solid var(--color-accent-secondary);
  padding-left: 16px;
  color: var(--color-text-secondary);
  margin: 1em 0;
}

.editor-textarea ul,
.editor-textarea ol {
  padding-left: 24px;
  margin: 0.5em 0;
}

.editor-textarea li { margin: 0.2em 0; }

.editor-textarea hr {
  border: none;
  border-top: 1px solid var(--color-bg-tertiary);
  margin: 1.5em 0;
}

.editor-textarea a { color: var(--color-accent-primary); }

/* Cursor */
.editor-textarea .ProseMirror-focused { outline: none; }

/* Placeholder */
.editor-textarea .is-empty::before {
  content: attr(data-placeholder);
  color: var(--color-text-muted);
  pointer-events: none;
  float: left;
  height: 0;
}
</style>
