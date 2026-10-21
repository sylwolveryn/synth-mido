---
id: TASK-003.01
title: Define light and dark UI color tokens
status: Done
assignee: []
created_date: '2026-10-21T16:11:00Z'
updated_date: '2026-10-21T19:49:00Z'
labels:
  - ui theme
dependencies: []
references:
  - ui.py
parent_task_id: TASK-003
priority: medium
type: feature
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Widgets currently mix default ttk colors with hardcoded canvas fills, so a theme switcher has nothing consistent to apply. Named light and dark palettes need to cover the window, surfaces, text, borders, accents, piano keys, and log before any restyle work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Light and dark palettes exist as named tokens covering window, surfaces, text, borders, accents, piano keys, and log
- [x] #2 Tokens can be applied from one place rather than literals scattered through widget construction
- [x] #3 Piano idle and active colors are tokens, not hardcoded values in draw or highlight paths
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
theme.py: LIGHT and DARK palette dicts with identical keys; ui.py draw_piano/highlight read colors from self.palette (no color literals left in ui.py).
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
