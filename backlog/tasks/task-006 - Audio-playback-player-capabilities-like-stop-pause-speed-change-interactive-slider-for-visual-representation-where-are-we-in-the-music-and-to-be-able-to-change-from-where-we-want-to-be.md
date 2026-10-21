---
id: TASK-006
title: 'Playback controls: stop, pause, speed and seek slider'
status: To Do
assignee: []
created_date: '2026-10-21T16:01:00Z'
updated_date: '2026-10-21T20:00:00Z'
labels:
  - feature
dependencies:
  - TASK-005
references:
  - playback.py
  - ui.py
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
- [ ] #1 While a recording is loaded, a player bar shows its name, the current position and total length (mm:ss), and a position slider that moves smoothly during playback
- [ ] #2 Play/Pause pauses and resumes: pausing silences sounding notes at once and keeps the position; resuming continues from the same point and restarts notes that should be sounding there
- [ ] #3 Stop ends playback and returns the position to the start; Leállítás and Minden hang ki behave the same way
- [ ] #4 Playback speed can be chosen (at least 0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x); changing it during playback takes effect immediately without jumping position
- [ ] #5 Clicking or dragging the position slider jumps to that point, whether playing or paused; notes that should be sounding at the new point start, and no note is left hanging
- [ ] #6 After playback ends the recording stays loaded, so Play starts it again from the beginning
- [ ] #7 Key highlighting stays in sync with what is sounding through pause, seek, speed change and stop
- [ ] #8 Controls are disabled or harmless when no recording is loaded
- [ ] #9 Unit tests cover pause/resume, seek (including into the middle of a held note), speed change and stop for the Player, with a fake clock and timer
- [ ] #10 readme describes the player controls
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
