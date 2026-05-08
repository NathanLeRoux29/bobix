# File Explorer Modal — Design Spec

**Date:** 2026-05-08
**Status:** Approved

## Overview

Redesign the Notes file explorer from a flat list modal into a proper navigable file explorer. The modal form factor is preserved; the internals are rebuilt to support folder navigation, breadcrumb, drag & drop, and global search.

## Architecture

The feature lives entirely in `FilesModal.vue` (complete rewrite) with two new store actions added to `stores/notes.ts`. No new components are needed.

**New store actions:**
- `moveNote(noteId: number, folderId: number | null)` — moves a note to a folder, or to root if null
- `moveFolder(folderId: number, parentId: number | null)` — moves a folder under another folder, or to root if null

**Local component state:**
- `currentFolderId: number | null` — the folder currently being viewed (null = root)
- `navStack: Array<{ id: number | null; name: string }>` — breadcrumb history stack
- `searchQuery: string` — current search input
- `dragState` — tracks the item being dragged and current drop target

## Layout

Top to bottom inside the modal:

1. **Header** — "Fichiers" title (left), × close button (right)
2. **Search bar** — single text input, filters globally across all notes and folders by name
3. **Breadcrumb** — `Accueil › Dossier › Sous-dossier`, each segment clickable to jump to that level. Hidden when search is active.
4. **Items list** — folders first, then notes. Each item is draggable.

## Navigation

- Clicking a folder enters it: `currentFolderId` updates, folder is pushed onto `navStack`
- Clicking a note opens it in a tab and closes the modal
- Clicking a breadcrumb segment pops the stack back to that level
- "Accueil" always navigates to root (`currentFolderId = null`)

## Search

- Input filters across all notes and folders (not limited to current folder)
- Results displayed as a flat list while search is active
- Breadcrumb is hidden during search
- Clearing the search restores normal folder navigation at the current level

## Drag & Drop

Implementation uses the native HTML5 drag API (`draggable`, `dragstart`, `dragover`, `drop`). No external library.

**Supported operations:**
- Drop a note onto a folder → `moveNote(noteId, folderId)`
- Drop a folder onto another folder → `moveFolder(folderId, parentId)` (blocked if target is a descendant of the dragged folder)
- Drop between items → reorder within the current level (local state only, not persisted)

**Visual feedback:**
- Dragged item becomes semi-transparent (`opacity: 0.4`)
- Folder target highlighted in blue on dragover
- Horizontal insertion line shown between items when reordering

## Context Menu

Right-click context menu preserved using `Teleport` to body. Menu varies by target:

- **Note** → Renommer, Supprimer
- **Folder** → Nouvelle note dedans, Nouveau sous-dossier, Renommer, Supprimer
- **Background (empty area)** → Nouvelle note, Nouveau dossier

## Error Handling

- Moving a folder into one of its own descendants is blocked client-side (walk the folder tree to detect cycles)
- Store actions call the existing API endpoints; on failure the store reverts optimistically updated state

## Out of Scope

- Persisting item sort order to the database (drag-to-reorder is display-only)
- Multi-select
- Keyboard navigation
