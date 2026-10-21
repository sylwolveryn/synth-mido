---
id: TASK-024
title: Game controllers as extra instruments with tabs and per-source key colours
status: To Do
assignee: []
created_date: '2026-10-21T23:58:00Z'
labels:
  - input
  - ui
  - audio
dependencies: []
priority: medium
type: feature
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Players want to jam with friends on game controllers next to the computer keyboard. Every detected game controller (USB or Bluetooth) becomes an additional instrument with its own sound; the instrument area gets tabs (Instrument 1 = keyboard/mouse, Instrument 2, 3 ... = controllers). Without a controller the second tab is still shown but disabled. To tell players apart, each source lights the piano keys in its own colour, and playback differs from live playing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Game controllers are detected at start and while running (hot-plug), without new required dependencies
- [ ] #2 The instrument area has tabs: Instrument 1 for keyboard/mouse, Instrument 2 always visible (disabled without a controller), and a further tab per extra connected controller
- [ ] #3 Each controller tab chooses its own instrument; the controller's buttons play notes, the D-pad shifts octave/key, and stick/trigger control velocity and sustain
- [ ] #4 Controller notes sound on their own MIDI channel, are recorded with their instrument and appear on the note bus
- [ ] #5 Keys are lit in a distinct colour per source: keyboard/mouse, each controller, MIDI input and playback; playback differs from live playing in every skin
- [ ] #6 Tests cover detection with a fake backend, button/axis mapping, channels, recording and the colour assignment
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
