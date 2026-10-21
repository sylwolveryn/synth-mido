---
id: TASK-023
title: Selectable piano effects matched to the appearance
status: To Do
assignee: []
created_date: '2026-10-21T23:58:00Z'
labels:
  - fx
  - ui
dependencies: []
priority: medium
type: feature
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The note effect above the keys is always the same flame. Each appearance should have its own matching effect (Volcano: fire, Sakura: cherry petals drifting away from the keys, Steampunk: steam puffs, ...), switched automatically with the appearance but still selectable by hand. Effects should be a plug-in style registry so new effects and skins are cheap to add.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An effect selector sits next to the appearance selectors and lists every registered effect
- [ ] #2 Changing the appearance switches to that skin's matching effect; the user can still pick another one
- [ ] #3 Volcano uses the current fire, Sakura drifting petals, Steampunk steam, and every one of the 17 skins has a matching effect
- [ ] #4 Effects are strategies in a registry with a shared interface, and a skin names its effect, so adding one needs no change to the view
- [ ] #5 Every effect stays within the frame budget (capped shapes, pooled canvas items) and works with the Effekt on/off switch
- [ ] #6 Tests cover the registry, the skin mapping and the behaviour of each effect
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
