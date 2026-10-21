---
id: TASK-018
title: Remove the debug playback buttons (Skála, Akkord, Bemutató, Minden hang ki)
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T22:47:00Z'
updated_date: '2026-10-21T23:18:00Z'
labels:
  - ui
  - chore
dependencies: []
modified_files:
  - progress/README.md
  - progress/task-018.md
  - readme.md
  - synth_mido/core/events.py
  - synth_mido/ui/app.py
  - synth_mido/ui/common.py
  - synth_mido/ui/playback_view.py
priority: low
type: chore
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Lejátszás row still has early test buttons: a C major scale, a C major chord, a short demo melody and 'Minden hang ki', which duplicates 'Leállítás'. They were debug helpers, clutter the row and keep dead code (sequences, demo constants) alive.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The Skála, Akkord, Bemutató and Minden hang ki buttons are gone from the Lejátszás section
- [x] #2 The scale, chord and demo sequence code and their constants are removed
- [x] #3 Leállítás still stops a playing record, the pedal and every sounding note
- [x] #4 Unit tests and the pre-commit gate pass
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove the four buttons from the Lejátszás actions row in ui/app.py
2. Delete play_scale/play_demo/play_chord/_end_chord/_play_sequence/_play_index/_release_then_next and the sequence-only state (playing, play_job, _stop_sequences) from ui/playback_view.py
3. Remove C_MAJOR_SCALE/C_MAJOR_CHORD/DEMO_MELODY from ui/common.py and events.DEMO if unused
4. Keep Leállítás = stop_playback (player stop + pedal up + panic)
5. Update tests/readme, run unit tests and a window smoke test
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed the Skála, Akkord, Bemutató and Minden hang ki buttons plus the sequence player, its state (playing, play_job), the scale/chord/demo constants and the DEMO note source. Leállítás (stop_playback) still stops the player, lifts the pedal and silences all notes. Verified: 196 unit tests, ruff, and a real-window smoke test (3/3).
<!-- SECTION:FINAL_SUMMARY:END -->
