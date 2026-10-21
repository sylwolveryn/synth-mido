---
id: TASK-008.04
title: Sustain pedal on the computer keyboard
status: To Do
assignee: []
created_date: '2026-10-21T19:51:00Z'
labels:
  - feature
dependencies:
  - TASK-008.02
references:
  - ui.py
  - tone_synth.py
  - recorder.py
parent_task_id: TASK-008
priority: low
type: feature
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A real piano has a sustain pedal that keeps notes ringing after the keys are released, which is essential for playing legato and chords. The computer keyboard needs an equivalent, so keyboard play sounds like the piano. The VEVOR piano sends its own pedal as MIDI control change 64.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Holding a dedicated key (e.g. Space) acts as the sustain pedal: released notes keep sounding until the pedal is released
- [ ] #2 Sustain works for on-screen mouse clicks as well as for computer-keyboard notes
- [ ] #3 Sustain is sent as MIDI CC 64 to a connected MIDI output, and the TASK-007 fallback keeps the notes ringing while the pedal is down
- [ ] #4 A running recording stores the notes with the length they actually sounded, including the sustained part, so playback sounds the same
- [ ] #5 Pedal state is visible in the UI; the pedal is released when the window loses focus and on Leállítás / Minden hang ki
- [ ] #6 Unit tests cover the sustain logic (note release with and without pedal, pedal release ending held notes)
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
