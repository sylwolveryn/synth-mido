---
id: TASK-010
title: Synthwave note visual effect when notes are played
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T20:17:00Z'
updated_date: '2026-10-21T20:28:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-009
references:
  - ui.py
  - piano_layout.py
modified_files:
  - visualizer.py
  - theme.py
  - test_visualizer.py
  - ui.py
  - readme.md
  - progress/task-010-fx-synthwave.png
  - progress/task-010-fx-dark.png
  - progress/task-010.md
  - progress/README.md
priority: medium
type: feature
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
With the Synthwave redesign (TASK-009) the app should also react visually to the music: every played note should light up the screen with a neon effect, like the visualisers of synth software and Synthesia-style rising notes. This makes playing (and listening back to recordings) more fun and gives instant feedback on what is sounding.

Design direction: a visualiser band directly above the 88-key piano, aligned with the keys. Each sounding note grows a neon bar upward from its key (cyan for white keys, magenta for black keys, brightness from velocity). When the note ends the bar detaches and keeps rising and fading as a trail. Short sparks appear on note start. The perspective-grid floor matches the TASK-009 banner. It must react to every note source: mouse, computer keyboard (including octave shift and sustain), live MIDI input, record playback and the demo buttons.

Tk constraint: everything is drawn on a Canvas with after() frames. The effect must never delay or block note timing, so the drawing has to be light and capped.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A visualiser band above the piano shows a neon bar rising from each sounding note, aligned with that key across the whole 88-key range
- [x] #2 Bar colour follows key type and theme (Synthwave neon colours, accent colours in the other themes), and brightness follows velocity
- [x] #3 When a note ends its bar keeps rising and fades out as a trail; a short spark marks each note start
- [x] #4 Every note source triggers it: mouse, computer keyboard (incl. octave shift and sustain), live MIDI input, record playback and the demo buttons
- [x] #5 The effect can be switched on and off in the UI, and the choice is remembered between runs
- [x] #6 Animation runs smoothly (about 30 fps or more) and only while something is visible, with a cap on drawn objects, so dense playing or fast playback does not slow down note timing
- [x] #7 The band rescales with the window and works at the minimum window size
- [x] #8 Unit tests cover the effect model (spawning, rising, fading, removal, object cap, key alignment) without a real window
- [x] #9 readme and a progress page show the effect with screenshots
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New Tk-free `visualizer.py`: a Visualizer model with note_on(note, velocity, t) / note_off(note, t), plus frame(now, width, height, key_span), which returns shapes (glow, bar, spark) with an intensity. A sounding note grows a bar up from its key; after note_off the bar detaches, keeps rising and fades over about 1.6 s. Each note start makes a few sparks. Bars and sparks are capped (oldest dropped). active tells whether anything is left to draw. A seeded RNG makes it deterministic in tests.
2. theme.py: generic load_setting/save_setting on the existing settings.json (the theme helpers keep their behaviour).
3. ui.py: a visualiser canvas between the octave row and the piano, with a static perspective floor in the grid colour. highlight() gets a velocity argument and feeds the visualiser, so every note source is covered: mouse, keyboard, sustain, live input, playback and demos. A 30 fps after() loop runs only while something is visible, deleting and redrawing the fx items each frame. Colours come from key_*_active mixed with the keybed by intensity, so all themes are covered. An "Effekt" checkbutton toggles it (the band is hidden and cleared when off) and is saved as visual_fx. The window grows to fit (860x930, minimum 780x790).
4. Tests `test_visualizer.py`: spawn, growth, detach and fade, removal, caps, key alignment, retrigger, plus the settings helpers.
5. Smoke test: all sources, toggle persistence, resizing, frame time under heavy load, screenshot.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified: 151 unit tests green (17 new visualizer and settings tests), ruff clean, real-window smoke test 15/15 covering every note source, sustain, idle stop, resize, toggle persistence. Performance: the first version took ~20 ms per frame under a 300-note burst. Canvas redraw was the bottleneck (~22 ms for 284 items). Fixes: pooled canvas items, stricter caps (96 bars, 60 sparks, 3 sparks per note) and an adaptive frame delay, giving ~12.7 ms under the same extreme load.

Correction: the full unit suite at that point was 150 tests, not 151.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
New Tk-free visualizer.py models the Synthwave note effect: each sounding note grows a neon bar from its key; on release the bar detaches, rises and fades over 1.6 s, with sparks on note start. Bars and sparks are capped. ui.py adds an fx band between the octave row and the piano, with a perspective grid floor in the theme grid colour. highlight() now takes velocity and feeds the visualiser, so mouse, computer keyboard (octave shift, sustain), live MIDI input, playback and demos all trigger it. A ~30 fps loop runs only while something is visible, reuses canvas items and slows itself down if a frame is slow. The Effekt checkbutton hides it and is saved via new theme.load_setting/save_setting. Window default 860x940 (min 780x800). 17 unit tests plus a smoke test with frame-time measurement.
<!-- SECTION:FINAL_SUMMARY:END -->
