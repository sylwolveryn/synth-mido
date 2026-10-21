---
id: TASK-013.02
title: 15 new skins, each with a dark and a light variant
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T20:51:00Z'
updated_date: '2026-10-21T21:08:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-013.01
modified_files:
  - groma/systems/synth-mido/components/catalog.md
  - groma/systems/synth-mido/components/painters.md
  - groma/systems/synth-mido/components/palette.md
  - groma/systems/synth-mido/components/registry.md
  - progress/README.md
  - progress/task-013-astronaut-dark.png
  - progress/task-013-gallery-dark.png
  - progress/task-013-gallery-light.png
  - progress/task-013-mathematics-light.png
  - progress/task-013-sakura-light.png
  - progress/task-013-steampunk-dark.png
  - progress/task-013.md
  - readme.md
  - synth_mido/skins/catalog.py
  - synth_mido/skins/painters.py
  - synth_mido/skins/palette.py
  - synth_mido/skins/registry.py
  - synth_mido/skins/theme.py
  - synth_mido/ui/app.py
  - synth_mido/ui/common.py
  - synth_mido/ui/fx_view.py
  - synth_mido/ui/input.py
  - synth_mido/ui/theming.py
  - tests/test_skins.py
  - tests/test_theme.py
  - tests/test_visualizer.py
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
- [x] #1 15 new skins are selectable, each with distinct dark and light palettes (30 new looks)
- [x] #2 Each skin draws its own header scene that fits its theme and rescales with the window
- [x] #3 Every palette passes the 4.5:1 contrast checks for text and buttons
- [x] #4 A progress page shows a gallery of all skins
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
For each of 15 skins: dark + light make_palette and a canvas header painter in painters.py (Strategy), registered in catalog.py. Verify contrast for all variants and painters at two widths; gallery contact sheets.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
15 new skins (Űrhajós, Szafari, Térkép, Matematika, Ókor, Óceán, Erdő, Szakura, Steampunk, Arcade, Art Deco, Sivatag, Sarkvidék, Vulkán, Jazz klub), each with distinct dark and light palettes (30 new looks), plus a light Synthwave. Every skin draws its own header scene from canvas primitives that scales with the window. All 34 palettes pass the 4.5:1 checks (unit tested). progress/task-013.md has dark and light gallery sheets and four full-size screenshots.
<!-- SECTION:FINAL_SUMMARY:END -->
