---
id: TASK-022
title: Instrument illustration in the Lejátszás section
status: To Do
assignee: []
created_date: '2026-10-21T22:47:00Z'
labels:
  - ui
  - fx
dependencies: []
priority: medium
type: feature
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Choosing one of 128 instruments from a combobox is dry. Showing a small, cute drawing of an animal playing the selected instrument (for example a fox on a flute) makes the choice visible and playful.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The Lejátszás section shows a drawing of an animal playing the currently selected instrument
- [ ] #2 Every General MIDI instrument family has its own pre-made animal and instrument; the drawing changes when the instrument changes
- [ ] #3 Drawings are made from canvas primitives (no image files) and follow the active skin colours
- [ ] #4 The illustration updates when a record changes the instrument and fits at the minimum window size
- [ ] #5 Unit tests check that every instrument maps to an illustration
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
