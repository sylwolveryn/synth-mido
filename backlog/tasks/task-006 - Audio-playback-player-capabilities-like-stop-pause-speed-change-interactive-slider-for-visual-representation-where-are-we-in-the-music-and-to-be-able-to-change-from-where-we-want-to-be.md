---
id: TASK-006
title: 'Playback controls: stop, pause, speed and seek slider'
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T16:01:00Z'
updated_date: '2026-10-21T20:05:00Z'
labels:
  - feature
dependencies:
  - TASK-005
references:
  - playback.py
  - ui.py
modified_files:
  - playback.py
  - test_playback.py
  - ui.py
  - readme.md
  - progress/task-006-player.png
  - progress/task-006.md
  - progress/README.md
priority: medium
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-005 added playback of saved recordings (playback.py Player, started from the "Felvétel lejátszása…" button or the Felvételek window), but a recording can only be played from start to end or cut off with Leállítás. To practise or listen back to part of a longer recording, the user needs real player controls: pause and resume, a different playback speed, and a position slider that shows where the playback is and lets them jump anywhere.

Context: the Player is driven by Tk after() callbacks and a clock, and sends notes through the shared output (TASK-007) with key highlighting. Playback is never recorded (TASK-004). Space is reserved for the sustain pedal (TASK-008.04), so it must not be used as the play/pause shortcut.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 While a recording is loaded, a player bar shows its name, the current position and total length (mm:ss), and a position slider that moves smoothly during playback
- [x] #2 Play/Pause pauses and resumes: pausing silences sounding notes at once and keeps the position; resuming continues from the same point and restarts notes that should be sounding there
- [x] #3 Stop ends playback and returns the position to the start; Leállítás and Minden hang ki behave the same way
- [x] #4 Playback speed can be chosen (at least 0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x); changing it during playback takes effect immediately without jumping position
- [x] #5 Clicking or dragging the position slider jumps to that point, whether playing or paused; notes that should be sounding at the new point start, and no note is left hanging
- [x] #6 After playback ends the recording stays loaded, so Play starts it again from the beginning
- [x] #7 Key highlighting stays in sync with what is sounding through pause, seek, speed change and stop
- [x] #8 Controls are disabled or harmless when no recording is loaded
- [x] #9 Unit tests cover pause/resume, seek (including into the middle of a held note), speed change and stop for the Player, with a fake clock and timer
- [x] #10 readme describes the player controls
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. playback.py: extend Player into a small transport. State: stopped / playing / paused, a position in record seconds and a speed factor. position() = base position + elapsed clock time * speed while playing. Note spans are kept besides the event list, so resume/seek can restart the notes that should be sounding at a position (start < pos < end) and continue from the first event at or after it. pause() releases sounding notes and keeps the position. play_pause() resumes, or restarts from 0 when at the end. seek(t) clamps to 0..duration and works while playing, paused or stopped. set_speed(x) re-bases the clock so the position does not jump. stop() releases notes and rewinds to 0 but keeps the record loaded. A note_off is only sent for notes that are actually sounding.
2. ui.py: player bar as a new row in the Lejátszás frame: Play/Pause and Stop buttons, record name, "mm:ss / mm:ss" label, a position slider (custom click/drag -> seek on release, so dragging does not retrigger notes) and a speed combobox (0.5x-2x). Refreshed every 100 ms while playing and after every action. Disabled until a record is loaded. The status bar shows Lejátszás / Szünet. Leállítás, Minden hang ki, demos and closing stop (rewind) the player.
3. Tests in test_playback.py: pause/resume, seek into a held note, seek while paused, speed change without a position jump, stop rewinds but keeps loaded, play after the end restarts.
4. readme player controls; progress page with a screenshot.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified: 83 unit tests green (28 playback, incl. 11 new transport tests), ruff clean, real-window smoke test without a MIDI device 19/19 (disabled before load, moving slider, pause silences, click-seek while paused, 2x speed, stop rewinds, restart after end, demo and player stop each other). Progress page: progress/task-006.md.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The Player in playback.py is now a transport: play/pause/stop, seek and speed (0.5x-2x), with the position kept in record time. Resume and seek restart the notes that should be sounding at that point, and note_off is only sent for sounding notes. ui.py has a player bar in the Lejátszás frame: play/pause, stop, record name, position slider (click/drag, seek on release), time label and speed selector, disabled until a record is loaded. Leállítás/Minden hang ki/demos/close stop and rewind it. Tests: 11 new Player tests; smoke-tested in the real window. Risk: the slider click mapping assumes an 8 px handle margin of the clam theme.
<!-- SECTION:FINAL_SUMMARY:END -->
