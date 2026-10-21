---
id: TASK-008.03
title: Octave shift and key labels for keyboard play
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T19:51:00Z'
updated_date: '2026-10-21T20:11:00Z'
labels:
  - feature
dependencies:
  - TASK-008.02
references:
  - ui.py
parent_task_id: TASK-008
priority: medium
type: feature
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A computer keyboard covers only about one and a half octaves, but the piano has 88 keys. The user needs to move the keyboard range up and down to reach the whole piano, and to see which piano keys the letter keys currently play.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Two dedicated keys (and matching buttons in the UI) shift the computer-keyboard range down and up by one octave
- [ ] #2 The range never goes outside A0-C8; at the ends the shift stops, and mapped notes beyond the edge are simply silent
- [ ] #3 The piano shows which keys the computer keyboard currently plays (highlighted range), and can show the letter label on each of those keys
- [ ] #4 The current octave or range is shown in the UI, and the default range starts around middle C (C4)
- [ ] #5 Shifting octave while keys are held does not leave hanging notes
- [ ] #6 Unit tests cover range shifting and its limits
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. keyboard_play.py: octave keys X (down) and C (up), the same physical keys on QWERTZ and QWERTY and not used for notes. KeyboardPlayer.shift(octaves) keeps the base between C0 (12) and C7 (96), so A0 and C8 are both reachable while out-of-range keys stay silent. Holding an octave key does not repeat. An on_range_change callback, range_notes() (the mapped notes clipped to A0-C8) and key_labels() (note -> letter, shown in Hungarian QWERTZ form: Z, É, Á) are added. Held notes keep their original note, so shifting never leaves notes hanging.
2. ui.py: a small row above the piano: ◀ button, range label (e.g. "C4–F5"), ▶ button and a "Betűk" checkbox. The canvas draws an accent bar over the mapped range and, when enabled, the letter on each mapped key. The window grows a little (default 860x760, minimum 780x660) so the log stays visible.
3. Tests: shift limits, X/C handling and no repeat, notes after shift, hanging-note safety, labels, range_notes at the ends.
4. Smoke test plus a progress page with screenshots at a low and a high octave.
<!-- SECTION:PLAN:END -->
