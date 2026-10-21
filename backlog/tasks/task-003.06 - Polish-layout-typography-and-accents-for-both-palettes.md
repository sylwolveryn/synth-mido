---
id: TASK-003.06
title: Polish layout, typography, and accents for both palettes
status: Done
assignee: []
created_date: '2026-10-21T16:12:00Z'
updated_date: '2026-10-21T16:49:00Z'
labels:
  - ui theme
dependencies:
  - TASK-003.05
references:
  - ui.py
parent_task_id: TASK-003
priority: low
type: enhancement
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Inverting colors is not enough for a designed window: the current form is dense default ttk with mixed fonts and a dark piano strip that may clash with a light palette. Spacing, type, and accents should look intentional in both Light and Dark while remaining readable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Spacing, fonts, and accent usage are consistent with the active palette
- [ ] #2 Light and Dark both keep readable contrast for labels, buttons, status, and log
- [ ] #3 Layout polish does not change connect, play, or listen behavior
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ui.py/theme.py: shared font family and size, bold muted LabelFrame titles, wider button padding, accent-styled Connect button, piano strip follows the palette. Contrast to be eyeballed manually.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
