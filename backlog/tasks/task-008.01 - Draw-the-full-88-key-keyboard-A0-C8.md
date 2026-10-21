---
id: TASK-008.01
title: Draw the full 88-key keyboard (A0-C8)
status: To Do
assignee: []
created_date: '2026-10-21T19:50:00Z'
labels:
  - feature
dependencies: []
references:
  - ui.py
parent_task_id: TASK-008
priority: medium
type: feature
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace the two-octave on-screen piano with the full 88-key range so every note a real piano can play can be seen and clicked. This is the base the computer-keyboard subtasks build on. 88 keys means 52 white keys, so at the current window size (860 px wide, 780 px minimum) each white key is only about 15-16 px wide. The layout must still be usable and clickable at that size.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The piano canvas draws MIDI notes 21 (A0) to 108 (C8): 52 white and 36 black keys in the correct pattern, starting with A0, A#0, B0 and ending on C8
- [ ] #2 All keys are visible at once at the default and the minimum window width, with no horizontal scrolling, and the keyboard rescales when the window is resized
- [ ] #3 Every key can be played and highlighted with the mouse, including black keys and the extreme keys A0 and C8
- [ ] #4 C keys carry octave labels (C1...C8) that stay legible at the default size; middle C (C4) is easy to find
- [ ] #5 Live MIDI input, record playback and the demo buttons highlight the correct key anywhere in the 88-key range
- [ ] #6 Both light and dark themes look correct on the new keyboard
- [ ] #7 Unit tests cover the key layout (note to white/black key and position mapping, 88 keys, range ends) without needing a real window
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
