---
id: TASK-003.03
title: Detect OS appearance and default to System
status: Done
assignee: []
created_date: '2026-10-21T16:12:00Z'
updated_date: '2026-10-21T16:49:00Z'
labels:
  - ui theme
dependencies:
  - TASK-003.02
references:
  - ui.py
parent_task_id: TASK-003
priority: medium
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users expect first launch to match Windows or Linux light/dark mode rather than a fixed vista or always-dark window. System mode should resolve from the current OS color scheme, with a safe fallback if that scheme cannot be read.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 System mode resolves to light or dark from the current OS color scheme
- [ ] #2 First launch with no saved preference uses System
- [ ] #3 If the OS scheme cannot be read, a documented fallback is used and the app does not crash
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
theme.py: detect_system_theme() (Windows registry, macOS defaults, Linux gsettings); any failure returns light (FALLBACK_SCHEME). Default mode is System.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
