---
id: TASK-003
title: >-
  add some cool Design to the UI, with dark, light and like OS system (also: as
  default) theme
status: To Do
assignee: []
created_date: '2026-10-21T15:59:00Z'
updated_date: '2026-10-21T16:11:00Z'
labels:
  - ui theme
dependencies: []
references:
  - ui.py
priority: medium
type: feature
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Tkinter window in ui.py still uses default ttk/vista styling plus hardcoded piano and canvas colors. There is no Light, Dark, or System appearance, so the app cannot match the OS on first launch or let the user pick a look. This parent tracks a themed UI that stays readable across ttk widgets, the canvas piano, and the MIDI log, without changing MIDI behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The app offers Light, Dark, and System appearance modes
- [ ] #2 System is the default when no saved preference exists
- [ ] #3 Changing the mode updates the whole window, including ttk widgets, the piano canvas, and the log
- [ ] #4 The chosen mode is restored on the next launch
- [ ] #5 Connect, play, and listen behavior is unchanged
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
