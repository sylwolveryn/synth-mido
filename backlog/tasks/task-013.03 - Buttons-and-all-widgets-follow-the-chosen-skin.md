---
id: TASK-013.03
title: Buttons and all widgets follow the chosen skin
status: To Do
assignee: []
created_date: '2026-10-21T20:51:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-013.01
parent_task_id: TASK-013
priority: high
type: feature
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Colours alone are not enough: buttons, sliders, checkbuttons, comboboxes, scrollbars, the log, dialogs, the piano keys, the visual effect and the equalizer window should all take their look from the skin: shape (padding, border width, relief), fonts, letter case of titles, and the colours of every state (hover, pressed, disabled, selected).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each skin defines widget style tokens (font family, title case, button padding/border/relief, accent per state) and every ttk widget style is built from them
- [ ] #2 Hover, pressed, disabled and selected states use skin colours (no default-grey Tk state left)
- [ ] #3 Dialogs (records window, save dialog), piano keys, keyboard range bar, visual effect and equalizer window use the skin
- [ ] #4 Switching skins at runtime restyles every open window without restart
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
