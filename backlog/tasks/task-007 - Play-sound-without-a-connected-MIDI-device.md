---
id: TASK-007
title: Play sound without a connected MIDI device
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T18:23:00Z'
updated_date: '2026-10-21T19:49:00Z'
labels:
  - feature
dependencies: []
references:
  - midi_controller.py
  - ui.py
  - midi-controller
  - desktop-ui
modified_files:
  - tone_synth.py
  - config.py
  - midi_controller.py
  - ui.py
  - test_audio_output.py
  - requirements.txt
  - .pre-commit-config.yaml
  - readme.md
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
- [x] #1 With no MIDI output connected, the on-screen piano and the scale, chord and demo buttons are audible through the computer default output
- [x] #2 On Windows the fallback uses the built-in Microsoft GS Wavetable Synth, and changing the instrument changes the sound
- [x] #3 On Linux/macOS (no built-in synth port) a generated tone is played through the default audio device; a missing audio library or device does not crash the app and is reported once in the log
- [x] #4 When a MIDI output is connected it is used instead of the fallback; disconnecting returns to the fallback without restarting the app
- [x] #5 All note output goes through one shared path, so record playback (TASK-005/006) is audible without a MIDI device without extra work
- [x] #6 The UI shows which output is active (connected device name, or the fallback) in the status bar
- [x] #7 Panic / stop silences the fallback output too, with no hanging notes
- [x] #8 Unit tests cover output selection (connected vs fallback) and the tone fallback without needing a real audio or MIDI device
- [x] #9 readme documents the fallback behaviour and any new dependency in requirements.txt
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New `tone_synth.py`: `ToneSynth` — a mido-port-like object (`send(msg)`, `close()`, `name`) that mixes simple decaying sine voices (numpy) into a sounddevice OutputStream on the default audio device. Handles note_on/note_off/all-notes-off (CC 120/123), ignores program_change. `render(frames)` is pure so it can be tested without an audio device; numpy/sounddevice are imported lazily so a missing library raises a clear error instead of crashing at import.
2. `config.py`: `FALLBACK_SYNTH_KEYWORDS` (Microsoft GS Wavetable, plus FluidSynth/TiMidity ports when a Linux user runs one).
3. `midi_controller.py`: one output path. `active_output` = connected output port, otherwise a lazily opened fallback (OS synth port matching the keywords, else ToneSynth). If neither is available, `fallback_error` is set once, and note sending is a silent no-op. All senders (note_on/off, chord, program change, panic) go through `_send`. `connect()` closes the fallback first (Windows GS synth can be the explicit output too). `close()` returns to the fallback lazily, and `shutdown()` also closes the fallback.
4. `ui.py`: sound buttons, on-screen piano and instrument change work without a connection; `require_output` checks for any active output. Status bar shows the active output (device name or "alapértelmezett" fallback); the fallback error is logged once; the instrument is re-applied after disconnect; on_close uses shutdown().
5. Tests `test_audio_output.py`: ToneSynth rendering/voices/all-notes-off without a device; controller output selection (GS port preferred, tone fallback, none → no crash + single error, connected output wins, disconnect returns to fallback) with mido mocked.
6. Pre-commit hook: run the new tests and install mido+numpy as `additional_dependencies` for the hook env. requirements.txt: numpy, sounddevice. readme: fallback section.
7. Verify: ruff, all unit tests, pre-commit, and an audible smoke test on this PC (GS synth fallback + forced tone fallback).
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented tone_synth.py (ToneSynth: numpy sine voices on a sounddevice stream, mido-port-like), FALLBACK_SYNTH_KEYWORDS in config.py, a single output path in midi_controller.py (active_output / _send, lazy fallback, connect closes the fallback, shutdown), and UI changes (sound without a connection, active output in the status bar, fallback error logged once). Added test_audio_output.py (19 tests), numpy/sounddevice in requirements.txt, hook deps, and a readme section. Verified: ruff clean, 55 unit tests green, pre-commit --all-files green, real-device smoke test on Windows (GS synth fallback, forced tone-generator fallback through the default speakers, panic, explicit connect to the GS synth while the fallback is open, return to the fallback on close). Not verified: Linux/macOS (no machine here).
<!-- SECTION:NOTES:END -->
