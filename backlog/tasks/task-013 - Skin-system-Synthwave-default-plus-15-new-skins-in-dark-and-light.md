---
id: TASK-013
title: 'Skin system: Synthwave default plus 15 new skins in dark and light'
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T20:50:00Z'
updated_date: '2026-10-21T21:09:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-012
priority: high
type: feature
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The app has four looks (Synthwave, System, Light, Dark). The user wants a skin system like Synthwave but with many more designs: 15 new themed skins, each in a dark and a light variant (30 new looks), e.g. astronaut/space, animals, maps, mathematics, history. Every skin needs its own palette, typography and a drawn header scene, and buttons and all other widgets must follow the chosen skin. Synthwave must be the default skin: the user still saw an older saved choice after TASK-009, so the new skin setting must start on Synthwave for everyone.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All subtasks are Done
- [x] #2 Synthwave is what the app opens with unless a skin was chosen under the new skin system
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Skin system delivered in 3 subtasks: registry-based skin engine with Synthwave dark as the enforced default (013.01), 15 new themed skins in dark and light (30 new looks) with canvas header scenes (013.02), and every widget, dialog and view styled from the skin (013.03). 167 unit tests green; real-window smoke tests and gallery screenshots in progress/task-013.md.
<!-- SECTION:FINAL_SUMMARY:END -->
