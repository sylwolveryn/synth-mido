---
id: TASK-022
title: Instrument illustration in the Lejátszás section
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T22:47:00Z'
updated_date: '2026-10-21T23:03:00Z'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. fx/instrument_art.py: 16 GM families mapped to an animal + instrument; Pen helper in 100x100 unit space; shared animal head/body builder with per-species traits; one drawer per instrument; colours from the skin palette; duck-typed canvas.
2. ui/instrument_view.py mixin: canvas next to the Megnyitás/Leállítás buttons with caption, redrawn on instrument change, record load, skin change and resize.
3. Tests: mapping for all 128 programs, every scene inside its box in all 34 looks, scaling, skin colours; real-window smoke at 780x800.
<!-- SECTION:PLAN:END -->
