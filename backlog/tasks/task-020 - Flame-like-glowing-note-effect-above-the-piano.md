---
id: TASK-020
title: Flame-like glowing note effect above the piano
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T22:47:00Z'
updated_date: '2026-10-21T23:18:00Z'
labels:
  - fx
  - ui
dependencies: []
modified_files:
  - progress/README.md
  - progress/task-020-flames.png
  - progress/task-020-skins.png
  - progress/task-020.md
  - readme.md
  - synth_mido/fx/visualizer.py
  - synth_mido/ui/app.py
  - synth_mido/ui/fx_view.py
  - tests/test_visualizer.py
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
- [x] #1 Each played note produces a glowing flame above its key that flickers while the note sounds and dies down after release
- [x] #2 Flames have a soft glow halo and rising embers instead of the small spark particles
- [x] #3 Flame colours follow the active skin (accent colours), velocity changes flame height
- [x] #4 Frame cost stays within the existing budget (capped shapes, pooled canvas items)
- [x] #5 The effect can still be switched off with Effekt; unit tests cover the model
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rewrite fx/visualizer.py as a flame model: per note a 3-layer halo, a flickering smoothed flame polygon and a bright core; velocity drives height/brightness; attack 80 ms, fade 0.55 s; embers burst on note-on and stream while held; caps 40 flames / 70 embers.
2. ui/fx_view.py: per-layer canvas pools (polygons/ovals), layer order halo, ember, flame, core restored only when items are created; colours from the skin sun gradient (dark/light variants).
3. Replace the bar/spark unit tests with flame tests; real-window smoke incl. frame cost and four-skin screenshot.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the neon bars and small sparks with glowing flames: a three-layer soft halo, a flickering smoothed flame tongue with a bright core, and embers rising from the tip while the note sounds. Velocity sets height and brightness; flames flare up in 80 ms and die down in about 0.5 s after release. Colours come from each skin's sun gradient, so every skin has its own fire. Canvas items stay pooled per layer with caps of 40 flames and 70 embers; measured 3.1 ms average per frame with 10 held notes. Verified by 15 model tests and a real-window smoke test (13/13) with screenshots in four skins.
<!-- SECTION:FINAL_SUMMARY:END -->
