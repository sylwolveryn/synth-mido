---
id: TASK-008.02
title: Play notes with the computer keyboard
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T19:50:00Z'
updated_date: '2026-10-21T20:11:00Z'
labels:
  - feature
dependencies:
  - TASK-008.01
references:
  - ui.py
modified_files:
  - keyboard_play.py
  - test_keyboard_play.py
  - ui.py
  - readme.md
  - progress/task-008-02-keyboard-chord.png
  - progress/task-008-02.md
  - progress/README.md
parent_task_id: TASK-008
priority: medium
type: feature
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Let the user play the on-screen piano from the computer keyboard, so melodies and chords can be played without a MIDI device or the mouse. The usual two-row layout used by music software (a lower row of letter keys for white keys, the row above for the black keys in between) feels like a piano. The user types on a Hungarian QWERTZ layout, where Y and Z are swapped compared with US QWERTY, so the mapping must make sense there.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A fixed set of letter keys plays at least one and a half octaves: one row for white keys, the row above for the matching black keys, laid out like a piano
- [x] #2 The mapping works on a Hungarian QWERTZ layout and on a US QWERTY layout
- [x] #3 Pressing a key starts the note and releasing it stops the note; holding a key does not retrigger it through key auto-repeat
- [x] #4 Several keys can be held at the same time to play chords
- [x] #5 Played keys are highlighted on the on-screen piano, and velocity comes from the Hangerő slider
- [x] #6 Notes sound through the active output (connected MIDI device or the TASK-007 fallback) and are captured by a running recording like on-screen clicks
- [x] #7 Typing in text fields (save dialog name, comboboxes) does not play notes, and no note is left hanging when the window loses focus
- [x] #8 Unit tests cover the key-to-note mapping for both layouts, without needing a real window
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New Tk-free `keyboard_play.py`: KEYMAP of Tk keysyms to semitone offsets in the usual two-row layout. Home row A S D F G H J K L ;/é and \x27/á are white keys C..F (+1 octave); the row above W E T Y/Z U O P holds the black keys. US QWERTY and Hungarian QWERTZ are both covered (y and z both map to G#; é/á for ;/\x27), giving 18 notes (C to F an octave up). `KeyboardPlayer` uses injected after/cancel and on_note. Repeated KeyPress of a held key is ignored (Windows auto-repeat); KeyRelease is deferred by ~30 ms and cancelled by an immediate re-press (X11 auto-repeat). It remembers the note per key, so a later octave shift cannot leave notes hanging. release_all() handles focus loss, and notes outside A0-C8 are silent. The base note defaults to C4.
2. ui.py: root-level KeyPress/KeyRelease bindings (only the main window; dialogs are separate toplevels). Ignored in Entry/Combobox widgets and with Ctrl/Alt. Comboboxes give focus back to the window after a selection. Keyboard and mouse notes share one _user_note_on/off path (sound through the active output, recorder, highlight). FocusOut of the window releases all keyboard notes. The piano frame title gives a short hint.
3. Tests `test_keyboard_play.py`: both layouts map to 0..17, case-insensitivity, unknown keys, auto-repeat on both platforms, chords, range clipping, release_all.
4. Smoke test with real key events (event_generate) in the window, plus a progress page.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified: 111 unit tests green (16 keyboard tests), ruff clean, real-window smoke test with generated Tk key events 12/12. Found and fixed: this Tk build reports é/á as the character keysym instead of eacute/aacute, so both forms (and ;/\x27 characters) are mapped.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
New Tk-free keyboard_play.py maps two keyboard rows to C4-F5 (18 notes) on both Hungarian QWERTZ and US QWERTY (y/z both G#, é/á and ;/\x27 for the same physical keys, as keysym names or characters). KeyboardPlayer filters Windows and X11 auto-repeat, remembers each key's note so releases never hang, and releases everything on focus loss. ui.py binds keys on the main window only, ignores text inputs/comboboxes and Ctrl/Alt, returns focus after combobox selections, and shares one note path with the mouse (output, recorder, highlight). 16 unit tests plus a key-event smoke test. Range shifting and key labels follow in TASK-008.03.
<!-- SECTION:FINAL_SUMMARY:END -->
