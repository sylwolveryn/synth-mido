---
id: TASK-017
title: 'Multi-octave play: choose several octaves to sound together'
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T21:52:00Z'
updated_date: '2026-10-21T21:55:00Z'
labels:
  - feature
dependencies:
  - TASK-011
modified_files:
  - progress/README.md
  - progress/task-017-octaves.png
  - progress/task-017.md
  - readme.md
  - synth_mido/core/doubling.py
  - synth_mido/ui/app.py
  - synth_mido/ui/piano_view.py
  - synth_mido/ui/theming.py
  - tests/test_doubling.py
priority: medium
type: feature
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-011 added a fixed two-hand doubling (±1 octave). The player wants more: like playing the same line with several hands, pick any set of octaves and every played note sounds in all of them at once. The control belongs in the piano row next to Effekt and Pedál. By default only the octave the keyboard currently plays (set with X / C) is selected, so nothing changes until the player ticks more octaves.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An "Oktávok" multiselect in the piano row lists the octaves C0-C7; by default only the current keyboard octave (X / C) is ticked
- [x] #2 Ticking more octaves makes every note played with the computer keyboard or the mouse also sound in each ticked octave (same velocity), skipping notes outside A0-C8
- [x] #3 The keyboard octave is always included and follows X / C; the extra octaves stay as ticked
- [x] #4 Works together with Duplázás, the sustain pedal and recording (all sounding notes are recorded), with no hanging notes when the selection or octave changes while keys are held; live MIDI input and playback are not multiplied
- [x] #5 The piano shows a marker for each extra ticked octave, and the dropdown label shows the selection
- [x] #6 The control follows the skin and the piano row still fits at the minimum window width in every skin
- [x] #7 Unit tests cover the octave selection and the resulting note offsets
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. core/doubling.py: targets() accepts extra offsets (dedup, A0-C8 range); OctaveSelection (C0-C7, the keyboard octave always included and following X/C, ticked extras, offsets relative to the keyboard octave, label); OctaveDoubler.set_extra_offsets. 2. UI: an Oktávok ttk.Menubutton with a checkbutton per octave next to Effekt; the shorter range label makes room; piano markers for extra octaves; menubutton/menu themed from the skin. 3. Tests and smoke test; readme and progress page.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Multi-octave play: an Oktávok dropdown (C0-C7 checkboxes) next to Effekt. By default only the keyboard octave (X/C) is ticked; ticking more makes every mouse or computer-keyboard note sound in all ticked octaves with the same velocity, skipping notes outside A0-C8. The keyboard octave is always included and follows X/C while extras stay. Built on the existing OctaveDoubler (offsets combined with Duplázás, deduplicated, reference-counted), so the sustain pedal, recording, highlighting and effects cover every note and nothing hangs when the selection changes while keys are held. Live input and playback are not multiplied. The piano shows thin markers for the extra octaves; the control is skinned and the row fits at 780 px in every skin. 5 unit tests, smoke test 19/19.
<!-- SECTION:FINAL_SUMMARY:END -->
