---
id: TASK-011
title: Two-hand octave doubling for played notes
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T20:17:00Z'
updated_date: '2026-10-21T20:29:00Z'
labels:
  - feature
dependencies: []
references:
  - ui.py
  - keyboard_play.py
  - sustain.py
modified_files:
  - doubling.py
  - test_doubling.py
  - ui.py
priority: medium
type: feature
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Much piano music sounds fuller when the same line is played in two octaves at once, like the left and right hand playing the same melody 8 keys (one octave) apart. On the computer keyboard or with the mouse this is impossible to do by hand. The user wants a switch that automatically adds the same note one octave lower and/or higher.

Design: an "Oktáv duplázás" selector with Ki (off, default), +1 oktáv, −1 oktáv and ±1 oktáv (both). It applies to notes the user plays in the app (mouse and computer keyboard). Physical MIDI input already sounds on the real piano, so it is not doubled. The doubled notes are real notes: they sound through the shared output (TASK-007), are highlighted, follow the sustain pedal (TASK-008.04) and are recorded (TASK-004), so playback sounds the same as what was heard.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An "Oktáv duplázás" selector offers Ki, +1 oktáv, −1 oktáv and ±1 oktáv; Ki is the default and the choice is remembered between runs
- [ ] #2 With doubling on, each mouse or computer-keyboard note also plays the same note 12 semitones away in the chosen direction(s), with the same velocity
- [ ] #3 Doubled notes are highlighted on the piano, follow the sustain pedal and stop exactly when the original note stops, with no hanging notes, including when the setting or the octave range changes while keys are held
- [ ] #4 Doubled notes that would fall outside A0-C8 are skipped silently
- [ ] #5 Overlapping notes (e.g. C4 held with +1 while C5 is also pressed) do not cut each other off: a note keeps sounding while any key still needs it
- [ ] #6 A running recording stores the doubled notes too, so playback sounds the same
- [ ] #7 Live MIDI input and record playback are not doubled
- [ ] #8 Unit tests cover the doubling logic (directions, range edges, overlapping and shared notes, setting change while held)
- [ ] #9 readme and a progress page describe the feature with a screenshot
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. New Tk-free `doubling.py`: MODES off / up / down / both (offsets (), (+12), (-12), (-12,+12)) with Hungarian labels. OctaveDoubler.press(source) returns the real notes to start (the source plus the doubles inside A0-C8), remembers them per source key and counts how many held keys need each real note. release(source) returns only the notes nobody needs any more, so a shared note (C4+1 while C5 is held) keeps sounding, and a release after a setting change stops exactly what was started.
2. ui.py: _user_note_on/_user_note_off (mouse and computer keyboard only) go through the doubler. Each real note goes through the existing path (pedal key_down/key_up, output, recorder, highlight and visual effect), so sustain, recording and the effect cover the doubles automatically. Live MIDI input and playback do not use this path, so they are not doubled. A "Duplázás" combobox in the Lejátszás row (Ki / +1 oktáv / −1 oktáv / ±1 oktáv) is saved as octave_doubling.
3. Tests `test_doubling.py`: directions, range edges, shared notes, mode change while held, repeated press.
4. Smoke test (doubled sound, highlight and effect, pedal, recording, octave shift, input/playback not doubled, persistence), screenshot, readme and progress page.
<!-- SECTION:PLAN:END -->
