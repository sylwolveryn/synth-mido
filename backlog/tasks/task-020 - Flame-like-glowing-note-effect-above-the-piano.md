---
id: TASK-020
title: Flame-like glowing note effect above the piano
status: To Do
assignee: []
created_date: '2026-10-21T22:47:00Z'
labels:
  - fx
  - ui
dependencies: []
priority: medium
type: feature
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The note effect above the keys shows bars with small sparks; it feels thin. Played notes should glow and burn like small flames so the effect is more fun, while staying light enough for the Tk canvas.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each played note produces a glowing flame above its key that flickers while the note sounds and dies down after release
- [ ] #2 Flames have a soft glow halo and rising embers instead of the small spark particles
- [ ] #3 Flame colours follow the active skin (accent colours), velocity changes flame height
- [ ] #4 Frame cost stays within the existing budget (capped shapes, pooled canvas items)
- [ ] #5 The effect can still be switched off with Effekt; unit tests cover the model
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
