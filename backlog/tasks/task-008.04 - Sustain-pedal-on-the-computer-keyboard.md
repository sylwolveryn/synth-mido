---
id: TASK-008.04
title: Sustain pedal on the computer keyboard
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T19:51:00Z'
updated_date: '2026-10-21T20:14:00Z'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New Tk-free `sustain.py` with SustainPedal. It tracks pedal state and notes whose key was released while the pedal was down. key_up(note) says whether the note should stop now. Pressing a sustained key again takes it out of the sustained set. Releasing the pedal stops all sustained notes through a callback.
2. keyboard_play.py: Space is the pedal key (on_pedal callback). Repeats are ignored, and the release is deferred and cancelled by a quick re-press (X11 auto-repeat). release_all also lifts the pedal.
3. midi_controller.py: sustain(on) sends CC 64 (127/0) through the shared output.
4. ui.py: mouse and keyboard note-offs go through the pedal, so a sustained note keeps sounding and stays highlighted, and the recorder gets the real end time. A "Pedál (Szóköz)" checkbutton shows the state and can latch the pedal with the mouse. Space on a focused button in the main window acts as the pedal instead of clicking it (dialogs keep normal Space). The pedal is released on focus loss, Leállítás / Minden hang ki and close.
5. Tests: SustainPedal logic, Space debounce, controller CC 64. Smoke test plus a progress page.
<!-- SECTION:PLAN:END -->
