---
id: TASK-003.05
title: Follow live OS theme changes in System mode
status: To Do
assignee: []
created_date: '2026-10-21T16:12:00Z'
labels:
  - ui theme
dependencies:
  - TASK-003.04
references:
  - ui.py
parent_task_id: TASK-003
priority: medium
type: feature
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
System as default is incomplete if the window stays on the launch-time scheme after the user changes Windows or Linux appearance. While System is selected, OS light/dark changes should restyle the app; explicit Light or Dark must not be overridden.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 While System is selected, an OS light/dark change updates the UI without restart
- [ ] #2 Explicit Light or Dark is not overridden by later OS appearance changes
- [ ] #3 Any OS-theme watcher is stopped when the window closes
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
