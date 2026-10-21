---
id: TASK-013.01
title: Skin engine with registry and Synthwave as default
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T20:51:00Z'
updated_date: '2026-10-21T21:08:00Z'
labels:
  - feature
  - design
dependencies: []
modified_files:
  - groma/systems/synth-mido/components/catalog.md
  - groma/systems/synth-mido/components/painters.md
  - groma/systems/synth-mido/components/palette.md
  - groma/systems/synth-mido/components/registry.md
  - progress/README.md
  - progress/task-013-astronaut-dark.png
  - progress/task-013-gallery-dark.png
  - progress/task-013-gallery-light.png
  - progress/task-013-mathematics-light.png
  - progress/task-013-sakura-light.png
  - progress/task-013-steampunk-dark.png
  - progress/task-013.md
  - readme.md
  - synth_mido/skins/catalog.py
  - synth_mido/skins/painters.py
  - synth_mido/skins/palette.py
  - synth_mido/skins/registry.py
  - synth_mido/skins/theme.py
  - synth_mido/ui/app.py
  - synth_mido/ui/common.py
  - synth_mido/ui/fx_view.py
  - synth_mido/ui/input.py
  - synth_mido/ui/theming.py
  - tests/test_skins.py
  - tests/test_theme.py
  - tests/test_visualizer.py
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
- [x] #1 Skins are registered in one registry (id, display name, dark and light variant, fonts, header painter) and the UI lists them from it
- [x] #2 The UI offers a skin selector and a Sötét/Világos switch; changes apply at runtime and are saved
- [x] #3 Synthwave (dark) is the default; an old saved theme value no longer overrides it
- [x] #4 Classic Rendszer/Világos/Sötét looks are still available
- [x] #5 Unit tests cover the registry, variant lookup, defaults and the settings migration
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Skin/WidgetStyle dataclasses and a registry (register/get/all_skins/by_name). A palette builder with contrast enforcement. theme.py keeps OS detection and settings; new keys skin/skin_variant so the old theme value no longer overrides Synthwave. UI: skin and variant comboboxes, set_skin applies at runtime and saves, System variant polling.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Skin engine: synth_mido/skins/registry.py (Skin, WidgetStyle, register/get/all_skins/by_name, VARIANTS dark/light/system), palette.py (make_palette from base colours with WCAG >= 4.5 enforcement), catalog.py (registrations), theme.py (OS detection, settings, load_skin/save_skin under new keys). The Megjelenés row now has skin + Sötét/Világos/Rendszer selectors applied at runtime and saved. Synthwave dark is the default and the legacy theme key is ignored, fixing the reported issue. The classic look remains as the Klasszikus skin. Verified by test_theme/test_skins and a 17/17 real-window smoke test.
<!-- SECTION:FINAL_SUMMARY:END -->
