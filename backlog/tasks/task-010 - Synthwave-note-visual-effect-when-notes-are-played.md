---
id: TASK-010
title: Synthwave note visual effect when notes are played
status: To Do
assignee: []
created_date: '2026-10-21T20:17:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-009
references:
  - ui.py
  - piano_layout.py
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
- [ ] #1 A visualiser band above the piano shows a neon bar rising from each sounding note, aligned with that key across the whole 88-key range
- [ ] #2 Bar colour follows key type and theme (Synthwave neon colours, accent colours in the other themes), and brightness follows velocity
- [ ] #3 When a note ends its bar keeps rising and fades out as a trail; a short spark marks each note start
- [ ] #4 Every note source triggers it: mouse, computer keyboard (incl. octave shift and sustain), live MIDI input, record playback and the demo buttons
- [ ] #5 The effect can be switched on and off in the UI, and the choice is remembered between runs
- [ ] #6 Animation runs smoothly (about 30 fps or more) and only while something is visible, with a cap on drawn objects, so dense playing or fast playback does not slow down note timing
- [ ] #7 The band rescales with the window and works at the minimum window size
- [ ] #8 Unit tests cover the effect model (spawning, rising, fading, removal, object cap, key alignment) without a real window
- [ ] #9 readme and a progress page show the effect with screenshots
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
