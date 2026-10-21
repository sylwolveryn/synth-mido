---
id: TASK-007
title: Play sound without a connected MIDI device
status: To Do
assignee: []
created_date: '2026-10-21T18:23:00Z'
labels:
  - feature
dependencies: []
references:
  - midi_controller.py
  - ui.py
  - midi-controller
  - desktop-ui
priority: medium
type: feature
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Today every sound in the app (on-screen piano, scale/chord/demo buttons, and soon record playback from TASK-005/006) is sent only to a MIDI output the user has explicitly connected with "Csatlakozás". Without that, the app is silent, so recordings can be made "blindly" (TASK-004) but not heard, and the app is useless without the VEVOR piano or another MIDI device.

Agreed behaviour: when no MIDI output is connected, sound goes to the computer's default output instead.
- Windows: the OS ships a built-in General MIDI synth exposed as a MIDI output port ("Microsoft GS Wavetable Synth"). It is real GM, so instrument changes keep working.
- Linux/macOS: there is no built-in GM synth port, so a simple generated tone is played through the default audio device (e.g. numpy + sounddevice). The tone does not change with the chosen instrument; this limitation is accepted.
- An explicitly connected MIDI output always wins over the fallback. Recording (TASK-004) is unaffected.

All app sounds use the fallback, not only record playback, so TASK-005/006 should send notes through the same output path and get the fallback for free.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 With no MIDI output connected, the on-screen piano and the scale, chord and demo buttons are audible through the computer default output
- [ ] #2 On Windows the fallback uses the built-in Microsoft GS Wavetable Synth, and changing the instrument changes the sound
- [ ] #3 On Linux/macOS (no built-in synth port) a generated tone is played through the default audio device; a missing audio library or device does not crash the app and is reported once in the log
- [ ] #4 When a MIDI output is connected it is used instead of the fallback; disconnecting returns to the fallback without restarting the app
- [ ] #5 All note output goes through one shared path, so record playback (TASK-005/006) is audible without a MIDI device without extra work
- [ ] #6 The UI shows which output is active (connected device name, or the fallback) in the status bar
- [ ] #7 Panic / stop silences the fallback output too, with no hanging notes
- [ ] #8 Unit tests cover output selection (connected vs fallback) and the tone fallback without needing a real audio or MIDI device
- [ ] #9 readme documents the fallback behaviour and any new dependency in requirements.txt
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
