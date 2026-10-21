---
id: TASK-008
title: 88-key digital piano with computer keyboard play
status: To Do
assignee: []
created_date: '2026-10-21T19:50:00Z'
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
- [ ] #1 The on-screen piano shows all 88 keys of a real piano, A0 to C8, with the correct white and black key pattern
- [ ] #2 The piano can be played from the computer keyboard as well as with the mouse, with and without a connected MIDI device
- [ ] #3 All subtasks are Done
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
