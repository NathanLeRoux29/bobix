# Application de gestion de notes et tâches avec assistant IA — Spécifications

**Date** : 2026-05-01
**Version** : 0.1.0-draft
**Statut** : Brouillon — en cours de réflexion

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture](#2-architecture)
3. [Stack technique](#3-stack-technique)
4. [Écran de salutation](#4-écran-de-salutation)
5. [Hub](#5-hub)
6. [Écran Notes](#6-écran-notes)
7. [Écran Tasks](#7-écran-tasks)
8. [Bob — L'assistant IA](#8-bob--lassistant-ia)
9. [Système de thèmes](#9-système-de-thèmes)
10. [Paramètres](#10-paramètres)
11. [Documentation](#11-documentation)
12. [Tests](#12-tests)
13. [Docker et déploiement](#13-docker-et-déploiement)

---

## 1. Vue d'ensemble

### Concept

Application desktop de gestion de notes et tâches avec assistant IA intégré nommé **Bob**. L'utilisateur dispose d'un hub personnalisable avec widgets, d'un éditeur de notes Markdown complet, et d'un module de tâches. Bob peut lire, écrire et créer du contenu dans l'application.

### Objectifs

- Application desktop fonctionnelle via Tauri
- Backend API moderne sur serveur (préparé pour mobile et multi-utilisateurs)
- Personnalisation complète de l'interface (thèmes, couleurs)
- Assistant IA configurable et puissant
- Documentation exhaustive (technique + utilisateur)
- Tests complets (unitaires + E2E)

### Public cible

- Utilisateurs individuels souhaitant organiser leurs notes et tâches
- Future extension : équipes/organisations avec comptes multi-utilisateurs

---

## 2. Architecture

### Architecture réseau

```
┌──────────────────────────┐     ┌──────────────────────────┐
│   App Desktop (Tauri)    │     │   App Mobile (Future)    │
│                          │     │                          │
│  - Hub                   │     │  - Hub (simplifié)       │
│  - Notes                 │     │  - Notes                 │
│  - Tasks                 │     │  - Tasks                 │
│  - Paramètres            │     │                          │
└────────────┬─────────────┘     └────────────┬─────────────┘
             │                               │
             │         HTTP REST             │
             └───────────────┬───────────────┘
                             │
                     ┌───────▼───────┐
                     │   Serveur     │
                     │               │
                     │  ┌─────────┐  │
                     │  │ FastAPI │  │
                     │  │   API   │  │
                     │  └────┬────┘  │
                     │       │       │
                     │  ┌────▼────┐  │
                     │  │PostgreSQL│  │
                     │  └─────────┘  │
                     └───────────────┘
```

**Note** : Le backend est stateless et prévu pour recevoir un système d'authentification. Chaque utilisateur aura ses propres notes, tâches et config. L'API expose des endpoints REST protégés.

### Base de données

**PostgreSQL** — Choisi pour sa robustesse et son support natif du multi-utilisateur future.

Structure des tables principale (sans auth pour l'instant) :
- `notes` — id, title, content, folder_id, is_favorite, created_at, updated_at
- `folders` — id, name, parent_id, created_at
- `tasks` — id, title, description, due_date, tag, is_focus, is_completed, created_at, updated_at
- `settings` — id, key, value (stockage clé/valeur pour les préférences)

---

## 3. Stack technique

| Couche | Technologie |
|--------|-------------|
| Frontend Desktop | Tauri 2.x + Vue 3 + TypeScript + Vite |
| Frontend Mobile (future) | À définir |
| Backend | Python + FastAPI |
| Base de données | PostgreSQL 15 |
| IA | Bob, modèle unique configurable (Anthropic, OpenAI, Ollama, custom) |
| Conteneurisation | Docker + Docker Compose |
| Tests E2E | Playwright |

### Structure des dossiers

```
/app
├── src/                          # Frontend Vue (Tauri)
│   ├── components/              # Composants Vue
│   ├── views/                   # Pages (Hub, Notes, Tasks, Settings)
│   ├── stores/                  # Pinia stores
│   ├── router/                  # Vue Router
│   └── __tests__/               # Tests unitaires
│
├── src-tauri/                   # Tauri (Rust)
│   ├── src/
│   └── Cargo.toml
│
├── backend/                     # FastAPI Python
│   ├── app/
│   │   ├── api/                # Routes (notes, tasks, settings)
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Logique métier
│   │   └── core/               # Config, dépendances
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/                        # Documentation
│   ├── specs/                  # Cahiers des charges (ce dossier)
│   ├── user-guide/             # Doc utilisateur (site web)
│   └── dev/                    # Doc technique détaillée
│
├── docker-compose.yml           # PostgreSQL + Backend (serveur)
├── SPEC.md                     # Ce document
└── CHANGELOG.md                # Historique des versions
```

---

## 4. Écran de salutation

### Description
Écran plein écran affiché au démarrage de l'application, avant le Hub. Affiche un message personnalisé à l'utilisateur.

### Fonctionnement

- **Affichage** : À chaque lancement de l'application (sauf si désactivé dans paramètres)
- **Option de désactivation** : Dans Paramètres > Profil, toggle "Afficher la salutation au démarrage"
- **Templates disponibles** (sélection dans Paramètres > Profil) :

| ID | Template | Exemple |
|----|----------|---------|
| `salut` | `Salut {nom} !` | Salut Marc ! |
| `bienvenue` | `Bienvenue {nom}` | Bienvenue Marc |
| `pret` | `{nom}, prêt à travailler ?` | Marc, prêt à travailler ? |
| `hello` | `Hello {nom} 👋` | Hello Marc 👋 |
| `bonjour` | `Bonjour {nom}, bonne {moment}` | Bonjour Marc, bonne matinée |

> **Note** : Le template `{moment}` affiche automatiquement "matinée", "après-midi" ou "soirée" selon l'heure. Le message est choisi aléatoirement parmi les templates si l'option "Aléatoire" est cochée.

### Interface

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                        ──────────────────                       │
│                                                                 │
│                         Salut Marc !                            │
│                                                                 │
│                        ──────────────────                       │
│                                                                 │
│                                                                 │
│                          [ Continuer → ]                        │
│                                                                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

- Fond : couleur de fond principal de l'app
- Texte : centré, grande police (48px+)
- Bouton "Continuer" : petit, en bas, ou clic n'importe où

### Paramètres associés

Dans **Paramètres > Profil** :
- Champ "Nom d'utilisateur"
- Dropdown "Template de salutation" (avec preview)
- Toggle "Salutation aléatoire"
- Toggle "Afficher la salutation au démarrage"

---

## 5. Hub

### Description
Dashboard principal modulable avec widgets. Premier écran après la salutation.

### widgets disponibles

| Widget | Position par défaut | Description |
|--------|---------------------|-------------|
| **Tasks Focus** | Gauche | Tâches cochées "Focus" (max 5-8) |
| **Notes récentes** | Centre | 4 dernières notes ouvertes/éditées |
| **Notes favorites** | Centre-droit | Notes favorites pour accès rapide |
| **Bob Chat** | Droite | Chat rapide avec Bob |

### Système de widgets

- Grille CSS ou drag-drop (vue-draggable ou similaire)
- Chaque widget possède :
  - Un bouton pour le masquant
  - Possibilité de le déplacer (drag-drop)
- Layout sauvegardé en base de données
- Extensions futures possibles (Spotify widget, etc.)

### Interface

```
┌─────────────────────────────────────────────────────────────────────┐
│  [Logo]  MonHub                    ⚙️ Paramètres          [?] Aide  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐  ┌──────────────────┐  ┌─────────────────────┐ │
│  │  Tasks Focus  │  │  Notes récentes   │  │     Bob Chat        │ │
│  │               │  │                  │  │                     │ │
│  │  ○ Task 1     │  │  📄 Note A       │  │  [Messages...]      │ │
│  │  ● Task 2 ✓   │  │  📄 Note B       │  │                     │ │
│  │  ○ Task 3     │  │  📄 Note C       │  │  ─────────────────  │ │
│  │               │  │  📄 Note D       │  │                     │ │
│  │               │  │                  │  │  [Écrire...]        │ │
│  └───────────────┘  └──────────────────┘  │                     │ │
│                                           │  ┌─────────────────┐│ │
│  ┌───────────────┐                       │  │   Envoyer →     ││ │
│  │ ⭐ Favoris    │                       │  └─────────────────┘│ │
│  │  📄 Note X    │                       └─────────────────────┘ │
│  │  📄 Note Y    │                                                │
│  └───────────────┘                                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Navigation

Depuis le Hub, l'utilisateur peut accéder à :
- **Notes** : via le bouton dans la barre ou en cliquant sur une note
- **Tasks** : via un bouton ou widget dédié
- **Paramètres** : icône ⚙️

---

## 6. Écran Notes

### Description
Interface d'édition de notes Markdown avec onglets et panel IA (Bob) sur la droite.

### Fonctionnalités principales

#### Éditeur Markdown

| Mode | Description |
|------|-------------|
| **Éditer** | Texte brut MD, pas de rendu en temps réel |
| **Aperçu** | Rendu MD en temps réel (WYSIWYG light) |

- Toggle entre les deux modes via un bouton
- Police : Fira Code (modifiable via paramètres)
- Support complet de la syntaxe Markdown

#### Explorateur de fichiers (modal)

- Bouton dans la barre du haut pour ouvrir la modal
- Structure :
  - Section "Favoris" en haut
  - Arborescence des dossiers
  - Clic sur une note = ouvre dans un nouvel onglet
- Bouton pour créer une nouvelle note

#### Organisation des notes

- **Dossiers** : Création, suppression, imbrication possible
- **Favoris** : Notes starées, affichées en haut de la modal
- **Recherche** : Filtre par titre de note

#### Ongletset stockage

- Notes ouvertes en onglets
- Fermer un onglet = fermer la note
- Si note non sauvegardée, prévenir avant de fermer
- Sauvegarde automatique (debounced)

### Interface

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Retour Hub   Mes Notes      [📁 Fichiers] [🔍] [⚙️] [+ Nouvelle]│
├───────────────────────────────────────────────────┬─────────────────┤
│                                                   │                 │
│  ┌─ ONGLETS ───────────────────────────────────┐  │    Bob          │
│  │ Idées apps ✕ │ Roadmap ✕ │                  │  │                 │
│  └─────────────────────────────────────────────┘  │  ─────────────  │
│                                                   │                 │
│  ┌─ ÉDITEUR ───────────────────────────────────┐  │  [Messages...]  │
│  │ [📝 Éditer] [👁 Aperçu]                     │  │                 │
│  │                                              │  │  ─────────────  │
│  │ # Mes idées d'applications                   │  │                 │
│  │                                              │  │  [Écrire...]    │
│  │ Voici une liste de choses à faire :         │  │                 │
│  │                                              │  │  ┌────────────┐ │
│  │ - [ ] Réfléchir au concept                   │  │  │ Envoyer →  │ │
│  │ - [ ] Créer les specs                       │  │  └────────────┘ │
│  │                                              │  │                 │
│  └──────────────────────────────────────────────┘  │  ┌────────────┐ │
│                                                   │  │ 📝 Écrire  │ │
│                                                   │  │ 📋 Tâche   │ │
│                                                   │  │ 📄 Nouvelle│ │
│                                                   │  │   note     │ │
│                                                   │  └────────────┘ │
│                                                   │                 │
└─────────────────────────────────────────────────────────────────────┘

Modal "Fichiers" (apparaît au clic sur [📁 Fichiers]) :

┌──────────────────────────────────────┐
│         📁 Mes fichiers              │
├──────────────────────────────────────┤
│  ⭐ Favoris                          │
│    📄 Notes importantes              │
│                                      │
│  📁 Work                             │
│    📄 Roadmap Q2                     │
│    📄 Réunions                       │
│                                      │
│  📁 Perso                            │
│    📄 Idées apps                     │
│    📄 Projets persos                 │
│                                      │
│  [✕ Fermer]          [Nouvelle note] │
└──────────────────────────────────────┘
```

### Actions de Bob dans le panel

| Action | Comportement |
|--------|--------------|
| **Répondre dans le chat** | Message dans la fenêtre Bob |
| **Écrire dans la note** | Insère du texte à l'emplacement du curseur |
| **Créer une tâche** | Crée une tâche pré-remplie dans le module Tasks |
| **Créer une note** | Ouvre une nouvelle note avec le contenu généré |

---

## 7. Écran Tasks

### Description
Module de gestion de tâches séparé des notes. Chaque tâche peut être cochée "Focus" pour apparaître dans le Hub.

### Champs d'une tâche

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `title` | string | Oui | Titre de la tâche |
| `description` | string | Non | Description détaillée |
| `due_date` | date | Non | Date d'échéance |
| `tag` | string | Non | Catégorie/tag |
| `is_focus` | boolean | Oui (défaut: false) | Afficher dans le Hub |
| `is_completed` | boolean | Oui (défaut: false) | Tâche terminée |

### Fonctionnalités

#### Liste des tâches
- Vue liste avec checkbox
- Tri par date d'échéance ou date de création
- Filtrer par tag/catégorie
- Filtrer par statut (Toutes, À faire, Terminées, Focus)
- Recherche par titre

#### Flag "Focus"
- Checkbox "Afficher dans le Hub"
- Une tâche focus = apparaît dans le widget Tasks Focus du Hub
- Maximum 5-8 tâches en focus (configurable dans paramètres)

#### Actions
- Créer une tâche
- Éditer une tâche (modal)
- Supprimer une tâche (avec confirmation)
- Marquer comme faite (checkbox)
- Toggle Focus

### Interface

```
┌─────────────────────────────────────────────────────────────────────┐
│  ← Retour Hub    Mes Tâches         [+ Nouvelle] [🔍] [⚙️]         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Filtres : [Toutes] [À faire] [Terminées] [Focus]   Tag: [Tous ▼]  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ [ ] Réfléchir au concept de l'app                [Focus] [✕] │  │
│  │     Échéance: 15 mai 2026                            🏷️ Work │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ [x] Créer les specs techniques                    [Focus] [✕] │  │
│  │     Terminée le 28 avril                               🏷️ Dev │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ [ ] Préparer la présentation                    [Focus] [✕]  │  │
│  │     Échéance: 20 mai 2026                           🏷️ Work │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Modal "Nouvelle/Édition Tâche" :

┌──────────────────────────────────────┐
│     Nouvelle Tâche                   │
├──────────────────────────────────────┤
│  Titre *                             │
│  ┌────────────────────────────────┐  │
│  │                                │  │
│  └────────────────────────────────┘  │
│                                      │
│  Description                         │
│  ┌────────────────────────────────┐  │
│  │                                │  │
│  └────────────────────────────────┘  │
│                                      │
│  Échéance                            │
│  ┌────────────────────────────────┐  │
│  │ 📅 Sélectionner une date      │  │
│  └────────────────────────────────┘  │
│                                      │
│  Tag                                 │
│  [Work ▼]  ou nouveau tag...        │
│                                      │
│  ☑ Afficher dans le Hub             │
│                                      │
│        [Annuler]    [Enregistrer]   │
└──────────────────────────────────────┘
```

---

## 8. Bob — L'assistant IA

### Description
Bob est l'assistant IA intégré à l'application. Disponible dans le Hub (chat rapide) et dans l'écran Notes (panel latéral avec accès au contexte de la note).

### Personnalité

- **Ton** : Chill mais professionnel — "le mec cool qui est hyper balèze"
- **Style** : Amical, décontracté dans la conversation, précis et fiable dans les réponses techniques
- **Avatar** : À définir (emoji, icône, ou illustration)

### Fonctionnalités

#### Chat
- Conversation en langage naturel
- Historique des messages dans la session (pas persisté entre les sessions pour l'instant)
- Indicateur "Bob écrit..." pendant les réponses

#### Context Awareness (dans Notes)
- Bob lit automatiquement le contenu de la note active
- L'utilisateur peut lui donner accès à d'autres notes
- Bob peut croiser plusieurs notes pour répondre

#### Actions de Bob

| Action | Description |
|--------|-------------|
| **Répondre dans le chat** | Message textuel dans la fenêtre |
| **Écrire dans la note** | Insère du texte à l'emplacement du curseur |
| **Créer une tâche** | Génère une tâche pré-remplie, l'utilisateur valide |
| **Créer une note** | Génère le contenu d'une nouvelle note, l'utilisateur valide |

#### Commandes spéciales
- `@bob lis ma note "Roadmap Q2"` — Donne accès à une note spécifique
- `@bob crée une tâche pour [description]` — Crée une tâche
- `@bob crée une note "Titre"` — Crée une note

### Configuration IA

Dans **Paramètres > Bob & IA** :
- **Provider** : Anthropic (Claude), OpenAI (GPT), Ollama (local), Custom
- **Clé API** : Champ sécurisé, stocké chiffré
- **Modèle** : Liste des modèles disponibles selon provider
- **Température** : Créativité des réponses (0-1)
- **Instructions système** : Personnalisation optionnelle du comportement

### Interface Chat Bob

```
┌─────────────────────────────────┐
│  Bob                    [⚙️]   │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────────────┐   │
│  │ Bob                     │   │
│  │ Salut ! Je peux t'aider │   │
│  │ à rédiger ta note,      │   │
│  │ créer des tâches ou     │   │
│  │ répondre à tes questions │   │
│  └─────────────────────────┘   │
│                                 │
│           ┌───────────────────┐ │
│           │ Oui, je veux bien │ │
│           │ de l'aide pour    │ │
│           │ la conclusion.    │ │
│           └───────────────────┘ │
│                                 │
│  ┌─────────────────────────┐   │
│  │ Bob                     │   │
│  │ Je t'aide à rédiger     │   │
│  │ une conclusion concise  │   │
│  │ pour cette section...   │   │
│  └─────────────────────────┘   │
│                                 │
├─────────────────────────────────┤
│ [Écrire...]              [Env]  │
├─────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐        │
│ │📝 Écrire│ │📋 Tâche │        │
│ └─────────┘ └─────────┘        │
└─────────────────────────────────┘
```

### Limites v1

- Historique du chat non persisté entre les sessions
- Pas de mémoire à long terme (pas d'accès aux notes sauf si explicitement demandé)

---

## 9. Système de thèmes

### Description
Personnalisation complète des couleurs de l'interface. Chaque composant peut avoir sa propre couleur, stockée comme variable CSS globale.

### Architecture

**Variables CSS globales** :
- Toutes les couleurs de l'app référencent ces variables
- Modifier une variable = mise à jour automatique de tous les composants
- Stockage en base de données (table `settings`)
- Injection dynamique au chargement de l'app

### Structure des couleurs

```css
:root {
  /* Fond */
  --color-bg-primary: #1a1a2e;
  --color-bg-secondary: #16213e;
  --color-bg-tertiary: #0f3460;

  /* Textes */
  --color-text-primary: #eaeaea;
  --color-text-secondary: #a0a0a0;
  --color-text-muted: #6c6c6c;

  /* Accents */
  --color-accent-primary: #e94560;
  --color-accent-secondary: #533483;

  /* États */
  --color-success: #4ade80;
  --color-warning: #fbbf24;
  --color-error: #ef4444;

  /* Composants */
  --color-button-bg: #e94560;
  --color-button-text: #ffffff;
  --color-input-bg: #16213e;
  --color-input-border: #0f3460;
  --color-panel-ia-bg: #1a1a2e;
  /* ... */
}
```

### Interface color picker

Dans **Paramètres > Apparence** :
- Liste des composants avec color picker
- Preview en temps réel
- Bouton "Réinitialiser" pour restaurer les valeurs par défaut

---

## 10. Paramètres

### Description
Écran de configuration de l'application accessible depuis le Hub.

### Catégories

#### 1. Profil
- Nom d'utilisateur (pour la salutation)
- Template de salutation
- Toggle salutation aléatoire
- Toggle afficher salutation au démarrage

#### 2. Apparence
- Personnalisation des couleurs (color picker par composant)
- Thèmes (sombre par défaut, clair future)
- Police de l'éditeur (Fira Code par défaut)

#### 3. Bob & IA
- Provider (Anthropic, OpenAI, Ollama, Custom)
- Clé API (champ sécurisé)
- Modèle à utiliser
- Température (0-1)
- Instructions système (optionnel)

#### 4. Raccourcis clavier (future)
- Liste des raccourcis clavier
- Personnalisation (future)

#### 5. À propos
- Version de l'application
- Liens (documentation, site, GitHub)
- Licences tierces

---

## 11. Documentation

### Structure

```
docs/
├── SPEC.md                         # Spécifications maître (ce document)
├── CHANGELOG.md                    # Historique des versions
│
├── specs/                          # Cahiers des charges détaillés
│   └── 2026-05-01-app-design.md   # Ce document
│
├── user-guide/                     # Documentation utilisateur (site web)
│   ├── index.md
│   ├── getting-started.md
│   ├── hub.md
│   ├── notes.md
│   ├── tasks.md
│   ├── bob.md
│   ├── settings.md
│   └── faq.md
│
└── dev/                            # Documentation technique
    ├── architecture.md            # Vue d'ensemble
    ├── frontend-structure.md      # Détail frontend Vue/Tauri
    ├── backend-structure.md       # Détail backend FastAPI
    ├── database-schema.md         # Schéma BDD détaillé
    ├── api-reference.md           # Référence API complète
    ├── docker.md                  # Setup Docker & déploiement
    ├── testing.md                 # Stratégie de tests
    └── contributing.md            # Guide de contribution
```

### Contenu CHANGELOG.md

Format inspiré de [Keep a Changelog](https://keepachangelog.com/) :

```markdown
# Changelog

## [0.1.0] — 2026-XX-XX

### Added
- Écran de salutation au démarrage
- Hub avec widgets configurables
- Module Notes avec éditeur Markdown (modes Éditer/Aperçu)
- Panel Bob dans l'écran Notes
- Système de thèmes avec color picker
- Paramètres utilisateur

### Fixed
- (aucun)

### Known Issues
- (liste des bugs connus)
```

### Documentation technique détaillée

Chaque document `dev/*.md` explique en détail :
- L'architecture du module
- Les fichiers importants et leur rôle
- Comment étendre ou modifier le module
- Les dépendances et interfaces

---

## 12. Tests

### Stratégie

#### Tests unitaires
- **Backend** : pytest sur les endpoints, services, et modèles
- **Frontend** : Vitest sur les composants Vue et les stores Pinia
- **Coverage target** : 80%+ du code

#### Tests fonctionnels (E2E)
- **Frontend** : Playwright
- **Scénarios** :
  - Créer, éditer, supprimer une note
  - Créer, éditer, compléter une tâche
  - Conversation avec Bob
  - Changement de thème
  - Navigation entre les écrans

#### Tests d'intégration
- **Backend** : pytest avec une vraie instance PostgreSQL (via Docker)
- Vérifient que les endpoints API fonctionnent correctement avec la BDD

### Couverture par module

| Module | Unit Tests | E2E |
|--------|------------|-----|
| Notes (CRUD) | ✅ | ✅ |
| Tasks (CRUD) | ✅ | ✅ |
| Bob Chat | ✅ (mock IA) | ✅ |
| Thèmes | ✅ | ✅ |
| Paramètres | ✅ | ✅ |
| Hub widgets | ✅ | ✅ |

### CI/CD
- GitHub Actions ou GitLab CI
- Lint + Type check à chaque PR
- Tests unitaires à chaque push
- Tests E2E sur PR avant merge

### Structure des tests

```
backend/
├── tests/
│   ├── unit/
│   │   ├── test_notes.py
│   │   ├── test_tasks.py
│   │   └── test_bob.py
│   └── integration/
│       └── test_api.py
│
src/
├── __tests__/
│   ├── components/
│   ├── stores/
│   └── e2e/
│       ├── notes.spec.ts
│       ├── tasks.spec.ts
│       └── bob.spec.ts
```

---

## 13. Docker et déploiement

### Structure Docker (Backend uniquement)

Le backend et la base de données sont déployés via Docker. L'application desktop est un binaire standalone.

#### Développement local

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://dev:dev_password@postgres:5432/myapp_dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - postgres

volumes:
  postgres_data:
```

#### Production

```yaml
# docker-compose.prod.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/myapp
      CORS_ORIGINS: ${CORS_ORIGINS}
    ports:
      - "8000:8000"
    restart: unless-stopped
    depends_on:
      - postgres

volumes:
  postgres_data:
```

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Variables d'environnement (production)

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | Mot de passe PostgreSQL |
| `CORS_ORIGINS` | URLs autorisées (frontend desktop) |
| `IA_PROVIDER` | Provider IA (Anthropic, OpenAI, etc.) |
| `IA_API_KEY` | Clé API IA (à sécuriser) |

### Architecture de déploiement future

```
┌─────────────────────────────┐       ┌─────────────────────────┐
│   Utilisateur               │       │   Serveur               │
│                             │       │                         │
│  ┌─────────────────────┐   │       │  ┌──────────────────┐   │
│  │  App Tauri (installée)│   │◄────►│  │  FastAPI (Docker)│   │
│  │  - Hub               │   │ HTTP │  │  - Bob           │   │
│  │  - Notes             │   │  s   │  │  - Notes API     │   │
│  │  - Tasks             │   │      │  │  - Tasks API     │   │
│  │  - Paramètres        │   │      │  └────────┬─────────┘   │
│  └─────────────────────┘   │       │           │             │
│                             │       │  ┌────────▼─────────┐   │
│                             │       │  │  PostgreSQL      │   │
│                             │       │  │  (Docker)        │   │
│                             │       │  └──────────────────┘   │
└─────────────────────────────┘       └─────────────────────────┘
```

---

## Annexe : Prochaines étapes

- [ ] Valider ces spécifications
- [ ] Créer le plan d'implémentation détaillé
- [ ] Initialiser le projet (repo, structure dossiers)
- [ ] Implémenter le backend FastAPI
- [ ] Implémenter le frontend Vue/Tauri
- [ ] Tests et documentation

---

*Document créé dans le cadre du projet de gestion de notes et tâches avec assistant IA.*