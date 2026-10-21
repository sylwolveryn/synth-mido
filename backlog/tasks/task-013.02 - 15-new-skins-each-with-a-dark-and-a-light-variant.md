---
id: TASK-013.02
title: 15 new skins, each with a dark and a light variant
status: To Do
assignee: []
created_date: '2026-10-21T20:51:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-013.01
parent_task_id: TASK-013
priority: high
type: feature
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add 15 themed skins in the spirit of Synthwave, each with a dark and a light palette and a drawn header scene: Astronaut (space), Safari (animals), Cartography (maps), Mathematics, Antiquity (history), Ocean, Forest, Sakura, Steampunk, Arcade, Art Deco, Desert, Arctic, Volcano and Jazz Club. Scenes are drawn with Tk canvas primitives (no image files) and must rescale with the window.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 15 new skins are selectable, each with distinct dark and light palettes (30 new looks)
- [ ] #2 Each skin draws its own header scene that fits its theme and rescales with the window
- [ ] #3 Every palette passes the 4.5:1 contrast checks for text and buttons
- [ ] #4 A progress page shows a gallery of all skins
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
