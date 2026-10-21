---
id: TASK-019
title: >-
  Record what is heard: mix playback into the take, record format version 2 with
  per-note instruments
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T22:47:00Z'
updated_date: '2026-10-21T22:49:00Z'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. core/recorder.py: VERSION 2 (V1 kept for reading and the songbook). Recorder tracks the current instrument (set_instrument), note_on/note_off take an optional instrument, held notes keyed by (program, note); stop() writes v2 notes with instrument {name, program}. validate_record accepts v1 and v2; helpers instruments_of / note_instrument; RecordInfo lists every instrument.
2. core/playback.py: spans/events carry the note's instrument (None for v1); repeats are cut per (instrument, note); Player calls on_note(note, velocity, on, instrument) and exposes sounding_voices() for a take started mid-playback.
3. audio: controller note_on/note_off/set_program take a MIDI channel; panic and sustain cover every used channel; ToneSynth keys voices by (channel, note).
4. ui: playing a v2 record assigns a channel per instrument (1..15, skipping drum channel 9) and sends program changes, leaving the user's instrument on channel 0 untouched; v1 keeps the old behaviour (main channel, selected instrument overridable). Player notes are fed into a running recording (v1 notes with the current main instrument); starting a take during playback captures the notes already sounding; instrument change updates the recorder.
5. songbook stays v1; tests for v2 shape, save/load/delete, v1 compatibility, mixing, per-instrument scheduling, channels; readme + progress page; smoke test in the real window.
<!-- SECTION:PLAN:END -->
