---
id: TASK-004
title: >-
  Add capability and UI buttons, for recording user input music play and save it
  to file under records
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T16:00:00Z'
updated_date: '2026-10-21T17:38:00Z'
labels: []
dependencies: []
references:
  - desktop-ui
  - ui.py
  - recorder.py
ordinal: 4000
---

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Goal: record what the user plays (the physical piano via the MIDI input, plus clicks on the on-screen piano) and save it as a Standard MIDI File (.mid) under `records/`. Saving as .mid means TASK-005/006 can load the file with `mido.MidiFile` and play it back with no custom format.

Research findings:
- ui.py `PianoApp` reads input only in `poll_midi()` (a 15 ms `after` loop), which runs only while "Figyelés" (listening) is on. On-screen clicks go through `on_piano_press/on_piano_release` -> `controller.note_on/note_off`.
- midi_controller.py has no recording logic, and no change to it is needed.
- Tests use unittest (test_theme.py). The pre-commit hook runs only `python -m unittest test_theme`.
- `records/` doesn't exist yet and isn't in .gitignore.

1. New module `recorder.py` (pure logic, no Tk) with class `MidiRecorder`:
   - `start()`, `stop()`, `is_recording`, `event_count`, `elapsed()`; takes an injectable clock (default `time.monotonic`) so it can be tested.
   - `add(msg)` stores (timestamp, copy of msg) for note_on/note_off/control_change (e.g. sustain pedal)/program_change, and ignores clock/active_sensing/sysex.
   - It tracks held notes. `stop()` appends note_off for any still-held notes so the file never has hanging notes.
   - `to_midifile()` builds a type-0 MidiFile: ticks_per_beat=480, a set_tempo meta of 500000 (120 BPM), and a program_change of the current instrument at t=0. Times use delta ticks from `mido.second2tick`, and the track ends with end_of_track.
   - `save(directory)` creates `records/` if needed, writes `felvetel_YYYYMMDD_HHMMSS.mid` (adding `_1`, `_2` on collision), and returns the Path. An empty recording isn't saved (returns None).
   - The `RECORDS_DIR` constant is the `records` folder next to the source files (Path(__file__).parent), so it doesn't depend on the cwd.
2. ui.py: add the recording UI.
   - In the "Billentyűzet figyelése" frame, next to the listen button: a "● Felvétel" / "■ Leállítás és mentés" toggle (Accent style while recording) and a muted label showing "00:12 · 34 esemény", refreshed every 250 ms while recording. There's no new LabelFrame, so the window height and minsize stay the same.
   - Starting a recording requires a connection. If there's an input port and listening is off, it starts listening automatically, because physical input is read only by `poll_midi`.
   - `poll_midi` passes each received message to `recorder.add()` while recording. `on_piano_press/on_piano_release` pass the on-screen note_on/note_off (with the current velocity and channel) to the recorder.
   - The scale/chord/demo buttons are NOT recorded, since only user-played input counts.
   - Stopping saves the file, logs the path, and shows it in the status bar. If nothing was played, it logs "Üres felvétel, nem mentve".
   - Disconnecting, closing the window, or a read error in `poll_midi` while recording stops and saves automatically, so nothing is lost.
   - The instrument chosen at recording start goes into the file as the program_change.
3. `.gitignore`: add `/records/`.
4. Tests in new `test_recorder.py` (unittest, fake clock, temp dir): event filtering, delta-tick timing, hanging notes closed on stop, the empty recording not saved, the filename pattern/collision suffix, and a round-trip save -> `mido.MidiFile` load giving the same notes in order with the right total length.
5. Add `test_recorder` to the pre-commit unit-test hook entry (`python -m unittest test_theme test_recorder`).
6. readme.md: a short "Felvétel" section on how to record and where files go.
7. Verify: ruff, `python -m unittest test_theme test_recorder -v`, and pre-commit run --all-files. Then a manual smoke test in the app: record a few on-screen clicks, stop, and check that the .mid appears under records/ and opens with mido.

Proposed acceptance criteria (to add once you approve):
- A record button starts and stops recording, with elapsed time and event count shown while recording.
- Notes from the physical MIDI input and from on-screen piano clicks are captured with their timing.
- Stopping saves a .mid file under records/ (timestamped name). An empty recording is not saved.
- A recording in progress is saved on disconnect or window close.
- The new unit tests run in pre-commit and pass.

Open questions:
- Should the scale/chord/demo buttons also be recorded? (Proposed: no.)
- Auto-save with a timestamped name (proposed), or a "Save as" dialog?
<!-- SECTION:PLAN:END -->
