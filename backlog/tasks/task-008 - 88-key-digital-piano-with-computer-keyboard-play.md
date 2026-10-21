---
id: TASK-008
title: 88-key digital piano with computer keyboard play
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T19:50:00Z'
updated_date: '2026-10-21T20:16:00Z'
labels:
  - feature
dependencies: []
references:
  - ui.py
  - desktop-ui
priority: medium
type: feature
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The on-screen piano in ui.py only draws two octaves (C3-C4, 25 keys: START_NOTE=48, OCTAVES=2), while the instrument it controls is a full 88-key ("88 billentyűs") digital piano (A0-C8, MIDI notes 21-108). Notes played on the real piano, or stored in a recording, that fall outside those two octaves are never highlighted and cannot be clicked. The app should show and play the whole range like the real instrument.

Today the on-screen piano can only be played with the mouse, one note at a time. Without the VEVOR piano attached, the user has no comfortable way to play melodies or chords, so the computer keyboard should work as a playing keyboard too. The subtasks split the work into: drawing the full 88-key keyboard, playing notes with the computer keyboard, moving the computer-keyboard range across the 88 keys (octave shift with labels), and a sustain pedal on the keyboard.

Constraints a future agent cannot see in the code: the user types on a Hungarian QWERTZ layout (Y and Z swapped compared with US QWERTY), so the key mapping must work there. Notes from the computer keyboard must go through the same paths as on-screen clicks: the shared output from TASK-007 (sound with or without a MIDI device) and the recorder from TASK-004 (playing can be recorded).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The on-screen piano shows all 88 keys of a real piano, A0 to C8, with the correct white and black key pattern
- [x] #2 The piano can be played from the computer keyboard as well as with the mouse, with and without a connected MIDI device
- [x] #3 All subtasks are Done
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
88-key digital piano with computer-keyboard play, delivered through 4 subtasks: full A0-C8 keyboard that scales with the window (008.01), two-row keyboard play on QWERTZ/QWERTY with auto-repeat filtering (008.02), octave shift with range bar and key letters reaching A0-C8 (008.03), and a Space sustain pedal that also sends CC 64 (008.04). All work goes through the shared output and recorder, with and without a MIDI device. 127 unit tests green; each subtask smoke-tested in the real window with screenshots under progress/.
<!-- SECTION:FINAL_SUMMARY:END -->
