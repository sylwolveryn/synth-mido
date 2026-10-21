---
id: TASK-008.02
title: Play notes with the computer keyboard
status: To Do
assignee: []
created_date: '2026-10-21T19:50:00Z'
updated_date: '2026-10-21T19:51:00Z'
labels:
  - feature
dependencies:
  - TASK-008.01
references:
  - ui.py
parent_task_id: TASK-008
priority: medium
type: feature
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Let the user play the on-screen piano from the computer keyboard, so melodies and chords can be played without a MIDI device or the mouse. The usual two-row layout used by music software (a lower row of letter keys for white keys, the row above for the black keys in between) feels like a piano. The user types on a Hungarian QWERTZ layout, where Y and Z are swapped compared with US QWERTY, so the mapping must make sense there.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A fixed set of letter keys plays at least one and a half octaves: one row for white keys, the row above for the matching black keys, laid out like a piano
- [ ] #2 The mapping works on a Hungarian QWERTZ layout and on a US QWERTY layout
- [ ] #3 Pressing a key starts the note and releasing it stops the note; holding a key does not retrigger it through key auto-repeat
- [ ] #4 Several keys can be held at the same time to play chords
- [ ] #5 Played keys are highlighted on the on-screen piano, and velocity comes from the Hangerő slider
- [ ] #6 Notes sound through the active output (connected MIDI device or the TASK-007 fallback) and are captured by a running recording like on-screen clicks
- [ ] #7 Typing in text fields (save dialog name, comboboxes) does not play notes, and no note is left hanging when the window loses focus
- [ ] #8 Unit tests cover the key-to-note mapping for both layouts, without needing a real window
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
