---
id: TASK-008.01
title: Draw the full 88-key keyboard (A0-C8)
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T19:50:00Z'
updated_date: '2026-10-21T20:06:00Z'
labels:
  - feature
dependencies: []
references:
  - ui.py
modified_files:
  - piano_layout.py
  - test_piano_layout.py
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New Tk-free `piano_layout.py`: the 88-key range (21-108), is_black(), note names, and `layout(width, height)`, which returns key rectangles (white keys evenly across the width, black keys centred on the white-key boundary, 60% wide and 62% high), plus `key_at(x, y)` with black keys on top.
2. ui.py: draw_piano uses the layout for the full range and rescales on <Configure>. Labels only on C keys (C1...C8), with middle C (C4) marked by an accent dot. Remove START_NOTE/OCTAVES; highlight() and mouse picking work for all 88 keys. Theme colours are unchanged.
3. Tests `test_piano_layout.py`: key count, range ends, white/black pattern, contiguous white keys, black-key placement, key_at, rescaling, label notes.
4. Smoke test in the real window: default and minimum width, clicks on A0/C8/black keys, live-input and playback highlighting across the range, both themes; progress page with screenshots.
<!-- SECTION:PLAN:END -->
