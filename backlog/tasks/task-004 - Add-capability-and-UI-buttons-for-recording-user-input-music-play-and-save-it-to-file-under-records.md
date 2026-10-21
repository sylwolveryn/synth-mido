---
id: TASK-004
title: >-
  Add capability and UI buttons, for recording user input music play and save it
  to file under records
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T16:00:00Z'
updated_date: '2026-10-21T18:03:00Z'
labels: []
dependencies: []
references:
  - desktop-ui
  - ui.py
  - recorder.py
modified_files:
  - recorder.py
ordinal: 4000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Recording can be started and stopped with a button, with or without a MIDI connection, and shows elapsed time and note count
- [ ] #2 Notes from the physical MIDI input and from on-screen piano clicks are captured with start time, duration and velocity
- [ ] #3 On stop the user can save under the default felvetel_YYYYMMDD_HHMMSS name or a custom name, or discard the take
- [ ] #4 Records are saved as JSON under records/ containing only notes, timing and the used instrument
- [ ] #5 A records view lists all records and can delete one or several selected records at once
- [ ] #6 Unit tests cover record shape/format, saving, loading and deleting, and pass in pre-commit
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Goal: record what the user plays (the physical piano via the MIDI input, plus clicks on the on-screen piano) and save it as a simple JSON record under `records/`, named by the user. Add a view that lists all records and can delete them one at a time or several at once. Recording works without a MIDI connection ("blindly").

Research findings:
- ui.py `PianoApp` reads input only in `poll_midi()` (a 15 ms `after` loop), which runs only while "Figyelés" (listening) is on. On-screen clicks go through `on_piano_press/on_piano_release`, which currently do nothing unless an output is connected.
- midi_controller.py has no recording logic, and no change to it is needed.
- Tests use unittest (test_theme.py). The pre-commit hook runs only `python -m unittest test_theme`.

Record format (JSON, UTF-8, one file per recording, `records/<name>.json`):
{
  "format": "synth-mido-record",
  "version": 1,
  "created": "2026-10-21T19:40:12",
  "instrument": {"name": "acoustic_grand_piano", "program": 0},
  "duration": 12.48,
  "notes": [
    {"note": 60, "velocity": 100, "start": 0.0, "duration": 0.42},
    ...
  ]
}
- Notes are already-paired events (start + duration in seconds, rounded to milliseconds, sorted by start), so replay in TASK-005/006 is a simple timed loop.
- "instrument" is only the default for replay. The player (TASK-005) may override it.
- Only notes, timing, and instrument are stored. No pedal/CC, no MIDI-file details.

1. New module `recorder.py` (pure logic + file storage, no Tk):
   - `RECORDS_DIR` is the `records` folder next to the source files (Path(__file__).parent / "records"), created on first save.
   - `Recorder(clock=time.monotonic)`: `start(instrument_name, program)`, `note_on(note, velocity)`, `note_off(note)` (note_on with velocity 0 counts as off), `stop() -> dict`, `is_recording`, `elapsed()`, `note_count`. `stop()` closes still-held notes at the stop time. A repeated note_on of an already-held note closes the previous one first.
   - `default_name(now=None)` returns `felvetel_YYYYMMDD_HHMMSS`.
   - `sanitize_name(name)` strips the `.json` suffix and whitespace, and replaces characters illegal in Windows/Linux filenames (`<>:"/\|?*` and control characters) with `_`. It raises ValueError if the result is empty or a reserved Windows name.
   - `validate_record(data)` checks the shape and types (format/version, instrument name+program 0–127, notes with note 0–127, velocity 1–127, start ≥ 0, duration ≥ 0) and raises ValueError with a readable Hungarian message.
   - `save_record(record, name, directory=RECORDS_DIR, overwrite=False) -> Path` validates, then writes indented JSON. It raises FileExistsError if the file exists and overwrite is False.
   - `load_record(path) -> dict` parses and validates, raising ValueError for bad JSON or a bad shape.
   - `list_records(directory=RECORDS_DIR) -> list[RecordInfo]` returns path, name, created, duration, note count, instrument, newest first. Unreadable or invalid files are still listed (marked "hibás") so they can be deleted.
   - `delete_records(paths, directory=RECORDS_DIR) -> int` deletes only `.json` files inside `directory`, refusing anything outside it, and returns the number deleted.
2. ui.py: recording controls in the "Billentyűzet figyelése" frame, next to the listen button:
   - A "● Felvétel" / "■ Leállítás" toggle (Accent style while recording), a "Felvételek…" button, and a muted label showing "00:12 · 34 hang", refreshed every 250 ms while recording.
   - Recording does NOT need a connection. If an input port is connected and listening is off, recording starts listening automatically so the physical piano is captured. Without any connection, only on-screen clicks are recorded (silently).
   - `on_piano_press/on_piano_release` record notes even when not connected; they still send sound only if an output is connected. Key highlighting works either way.
   - `poll_midi` passes note_on/note_off to the recorder while recording.
   - The scale/chord/demo buttons are not recorded.
   - The instrument currently selected in the "Hangszer" combo is stored in the record.
3. ui.py: save dialog after stopping (a modal themed Toplevel):
   - A name entry prefilled with `felvetel_YYYYMMDD_HHMMSS`, plus "Mentés" and "Elvetés" (discard / delete the take) buttons.
   - If the name already exists, it asks before overwriting. An invalid name shows the validation message and keeps the dialog open.
   - Closing the dialog with X counts as Elvetés, after confirmation.
   - If nothing was played, it logs "Üres felvétel, nem mentve" and shows no dialog.
   - Closing the app or disconnecting while recording stops the recording and opens the same dialog first, so nothing is lost silently.
4. ui.py: "Felvételek" window (a non-modal Toplevel, only one open at a time):
   - A ttk.Treeview with columns Név, Létrehozva, Hossz, Hangok, Hangszer, and `selectmode="extended"` (Ctrl/Shift multi-select).
   - Buttons: "Törlés" (deletes the selected records after a confirm showing the count), "Összes kijelölése", "Frissítés", and "Mappa megnyitása" (os.startfile / xdg-open), plus the Delete key as a shortcut for Törlés.
   - The list refreshes automatically after a new save.
   - The theme is applied: Treeview/Heading styles go into `apply_theme`, and open Toplevels get re-themed on theme change.
5. Tests in new `test_recorder.py` (unittest, fake clock, temp directory):
   - A record created by Recorder has exactly the expected keys/types/ranges, notes sorted, timing from the fake clock, held notes closed on stop, and instrument stored.
   - save -> file exists with the expected JSON -> load returns an equal record. The default name pattern is correct, overwrite protection works, and sanitize_name works.
   - Invalid files (bad JSON, missing keys, out-of-range values) are rejected by load_record.
   - list_records shows saved records (newest first) and marks broken ones.
   - delete_records removes one file, removes several at once, and refuses paths outside the records directory.
6. Add `test_recorder` to the pre-commit unit-test hook entry (`python -m unittest test_theme test_recorder`).
7. readme.md: a short "Felvétel" section covering recording, naming, the records list and deleting, and the JSON format.
8. Verify: ruff, `python -m unittest test_theme test_recorder -v`, and pre-commit run --all-files. Then a manual smoke test without a connection: click notes, stop, save under a custom name, see it in Felvételek, and delete one and then several.

Not in scope (per review): `.gitignore` is not changed. Playback of records belongs to TASK-005/006.

Proposed acceptance criteria (to add once you approve):
- Recording can be started and stopped with a button, with or without a MIDI connection, and shows elapsed time and note count.
- Notes from the physical MIDI input and from on-screen clicks are captured with start time, duration, and velocity.
- On stop, the user can save under a default `felvetel_YYYYMMDD_HHMMSS` name or a custom name, or discard the take.
- Records are saved as JSON under records/ containing only notes, timing, and the instrument used.
- A records view lists all records and can delete one or several selected records.
- Unit tests cover the record shape/format, saving, loading, and deleting, and pass in pre-commit.
<!-- SECTION:PLAN:END -->
