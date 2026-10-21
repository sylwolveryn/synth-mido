---
id: TASK-003.04
title: Add Light, Dark, and System theme selector and persist it
status: Done
assignee: []
created_date: '2026-10-21T16:12:00Z'
updated_date: '2026-10-21T19:49:00Z'
labels:
  - ui theme
dependencies:
  - TASK-003.03
references:
  - ui.py
parent_task_id: TASK-003
priority: medium
type: feature
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After System as the default, users still need an explicit Light, Dark, or System control that survives restarts. The control has to stay usable in both palettes and apply immediately.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A UI control lets the user choose Light, Dark, or System
- [x] #2 The chosen mode takes effect immediately
- [x] #3 The chosen mode is persisted and restored on the next launch
- [x] #4 The control remains usable in both light and dark palettes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ui.py: 'Megjelenés' combobox (Rendszer/Világos/Sötét) applies immediately and saves via theme.save_mode to the user config dir (%APPDATA%\synth-mido\settings.json or ~/.config/synth-mido/settings.json).
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
