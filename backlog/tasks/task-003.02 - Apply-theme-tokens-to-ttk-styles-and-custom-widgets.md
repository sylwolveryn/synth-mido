---
id: TASK-003.02
title: Apply theme tokens to ttk styles and custom widgets
status: Done
assignee: []
created_date: '2026-10-21T16:12:00Z'
updated_date: '2026-10-21T16:49:00Z'
labels:
  - ui theme
dependencies:
  - TASK-003.01
references:
  - ui.py
parent_task_id: TASK-003
priority: medium
type: feature
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
LabelFrames, comboboxes, buttons, the scale, the Text log, and the piano canvas do not consume a shared palette, so choosing a theme would only partially restyle the window. Existing widgets need to take colors from the active tokens, including a switch without restarting the app.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ttk widgets use styles derived from the active palette
- [ ] #2 Canvas piano background, keys, outlines, and labels use the active palette
- [ ] #3 Log Text widget colors match the active palette
- [ ] #4 Changing the active palette restyles already created widgets without restarting
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ui.py: PianoApp.apply_theme() switches ttk to clam, configures ttk styles, recolors root, canvas, log Text and combobox dropdown lists, then redraws the piano.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
