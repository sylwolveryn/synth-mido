---
id: TASK-013.01
title: Skin engine with registry and Synthwave as default
status: To Do
assignee: []
created_date: '2026-10-21T20:51:00Z'
labels:
  - feature
  - design
dependencies: []
parent_task_id: TASK-013
priority: high
type: feature
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the fixed theme modes with a skin registry: each skin is a named definition (palette tokens, font preference, header painter) in a dark and a light variant, registered by id. The Megjelenés selector becomes a skin selector plus a Sötét/Világos variant switch. The setting is stored under a new key so every user starts on Synthwave once; the old System/Light/Dark looks remain available as skins.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Skins are registered in one registry (id, display name, dark and light variant, fonts, header painter) and the UI lists them from it
- [ ] #2 The UI offers a skin selector and a Sötét/Világos switch; changes apply at runtime and are saved
- [ ] #3 Synthwave (dark) is the default; an old saved theme value no longer overrides it
- [ ] #4 Classic Rendszer/Világos/Sötét looks are still available
- [ ] #5 Unit tests cover the registry, variant lookup, defaults and the settings migration
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
