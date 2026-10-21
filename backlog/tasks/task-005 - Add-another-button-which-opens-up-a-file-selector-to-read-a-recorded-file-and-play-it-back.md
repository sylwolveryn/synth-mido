---
id: TASK-005
title: >-
  Add another button which opens up a file selector to read a recorded file and
  play it back
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T16:01:00Z'
updated_date: '2026-10-21T19:41:00Z'
labels:
  - feature
dependencies:
  - TASK-004
  - TASK-007
references:
  - recorder.py
  - ui.py
  - midi_controller.py
  - desktop-ui
modified_files:
  - playback.py
  - test_playback.py
priority: medium
type: feature
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-004 lets the user record what they play and save it as JSON under records/ (format: recorder.py, notes with start/duration/velocity plus the instrument used), and the "Felvételek" window can list and delete records, but there is no way to listen to a recording. This task adds playback of a saved recording, so the user can hear back what they played.

Agreed behaviour:
- Two entry points: a button in the main window that opens a file selector (for any record file), and playback straight from the Felvételek window.
- The instrument stored in the record is only the default: loading a record selects it in the Hangszer list, and the user may switch to another instrument before or during playback.
- Played notes light up on the on-screen piano, like the demo melody and live input do.
- Sound goes through the shared output path from TASK-007, so playback works with a connected MIDI device or, without one, through the computer default output.

Out of scope (TASK-006): pause/resume, speed change and the position/seek slider. Here the existing Leállítás and Minden hang ki buttons are enough to stop playback.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A "Felvétel lejátszása…" button in the main window opens a file selector that starts in records/ and shows .json record files
- [ ] #2 The Felvételek window has a "Lejátszás" button, and double-clicking a row plays that record; with no or multiple rows selected the button explains that one record must be selected
- [ ] #3 An unreadable or invalid record file is rejected with a readable error message and nothing is played
- [ ] #4 Loading a record selects its instrument in the Hangszer list; changing the instrument before or during playback takes effect
- [ ] #5 Notes play with their recorded start times, durations and velocities, in order, including overlapping notes and repeated notes
- [ ] #6 Playback works without a connected MIDI device (through the TASK-007 fallback) as well as with a connected MIDI output
- [ ] #7 Played notes are highlighted on the on-screen piano and un-highlighted when they end; notes outside the drawn keyboard play without errors
- [ ] #8 The log and status bar show which record is playing and when playback has finished
- [ ] #9 Leállítás and Minden hang ki stop playback immediately with no hanging notes; disconnecting or closing the app during playback stops it cleanly
- [ ] #10 Starting a playback while another sequence (scale, chord, demo or a record) is playing stops the previous one first, so sounds never overlap
- [ ] #11 Playback is not captured by a running recording (only notes the user plays are recorded)
- [ ] #12 Unit tests cover turning a loaded record into a timed note-on/note-off schedule (ordering, overlapping and repeated notes) and the default instrument, without Tk, MIDI or audio devices
- [ ] #13 readme describes how to play back a recording
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New `playback.py` (no Tk): `build_schedule(record)` turns notes into time-ordered note_on/note_off events (note_off before note_on at equal times; an overlapping repeat of the same pitch cuts the earlier note so it can not be silenced early); `default_instrument(record, instruments)` resolves the record instrument by name, then by program, else the first one; `Player` drives the schedule with injected `after`/`cancel` callbacks and a clock (catches up against the clock, so no drift), calls `on_note(note, velocity, on)` and `on_finish()`, and `stop()` releases sounding notes. This also gives TASK-006 a place for pause/speed/seek.
2. `ui.py`: "Felvétel lejátszása…" button in the Lejátszás row (file selector starting in records/, *.json); "Lejátszás" button and double-click in the Felvételek window (exactly one selected). Loading validates with `recorder.load_record` (error dialog on failure), selects the record instrument in the Hangszer list, and plays through the controller (TASK-007 shared output) with key highlighting. The recorder is bypassed, so playback is never recorded. Status bar and log show the playing record and the end; the status bar then returns to the output status.
3. One playback at a time: scale/chord/demo/record start by stopping whatever plays (`stop_playback(quiet=True)`) instead of being refused; Leállítás, Minden hang ki, disconnect and close stop the player too.
4. `test_playback.py`: schedule ordering, overlapping and repeated notes, empty record, default instrument, and Player timing/stop/finish/restart with a fake clock and fake `after`. Add it to the pre-commit unit-test hook.
5. readme: playback section.
6. Verify: ruff, all unit tests, pre-commit, and a scripted smoke test of the real window without a MIDI device (file playback, records-window playback, invalid file, instrument default, stop, replace, not recorded).
<!-- SECTION:PLAN:END -->
