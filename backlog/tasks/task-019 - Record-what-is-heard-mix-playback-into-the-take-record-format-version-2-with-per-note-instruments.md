---
id: TASK-019
title: >-
  Record what is heard: mix playback into the take, record format version 2 with
  per-note instruments
status: To Do
assignee: []
created_date: '2026-10-21T22:47:00Z'
labels:
  - recording
  - playback
  - audio
dependencies: []
priority: high
type: feature
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A recording only captures the notes the user plays. When the user plays along with a record, the take should contain everything that sounded: the replayed record and the user's notes meshed together. Records then need several instruments at once, so the JSON format gets a version 2 where every note names its instrument; version 1 files (current recordings and the songbook) must keep loading and playing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 New recordings are saved as version 2: every note has its own instrument (name and General MIDI program)
- [ ] #2 Version 1 records still load, validate, list and play exactly as before
- [ ] #3 While recording, notes from a playing record are captured together with the user's notes and live MIDI input
- [ ] #4 A version 2 record plays each note with its own instrument, simultaneously, without changing the user's selected instrument
- [ ] #5 The user can play along on the selected instrument while a version 2 record plays its own instruments
- [ ] #6 Changing the instrument during a take records later notes with the new instrument
- [ ] #7 Tests cover the version 2 shape, save/load/delete, v1 compatibility, mixing and multi-instrument playback
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
