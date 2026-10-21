---
id: TASK-018
title: Remove the debug playback buttons (Skála, Akkord, Bemutató, Minden hang ki)
status: To Do
assignee: []
created_date: '2026-10-21T22:47:00Z'
labels:
  - ui
  - chore
dependencies: []
priority: low
type: chore
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Lejátszás row still has early test buttons: a C major scale, a C major chord, a short demo melody and 'Minden hang ki', which duplicates 'Leállítás'. They were debug helpers, clutter the row and keep dead code (sequences, demo constants) alive.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The Skála, Akkord, Bemutató and Minden hang ki buttons are gone from the Lejátszás section
- [ ] #2 The scale, chord and demo sequence code and their constants are removed
- [ ] #3 Leállítás still stops a playing record, the pedal and every sounding note
- [ ] #4 Unit tests and the pre-commit gate pass
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
