---
id: TASK-017
title: 'Multi-octave play: choose several octaves to sound together'
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T21:52:00Z'
labels:
  - feature
dependencies:
  - TASK-011
priority: medium
type: feature
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-011 added a fixed two-hand doubling (±1 octave). The player wants more: like playing the same line with several hands, pick any set of octaves and every played note sounds in all of them at once. The control belongs in the piano row next to Effekt and Pedál. By default only the octave the keyboard currently plays (set with X / C) is selected, so nothing changes until the player ticks more octaves.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An "Oktávok" multiselect in the piano row lists the octaves C0-C7; by default only the current keyboard octave (X / C) is ticked
- [ ] #2 Ticking more octaves makes every note played with the computer keyboard or the mouse also sound in each ticked octave (same velocity), skipping notes outside A0-C8
- [ ] #3 The keyboard octave is always included and follows X / C; the extra octaves stay as ticked
- [ ] #4 Works together with Duplázás, the sustain pedal and recording (all sounding notes are recorded), with no hanging notes when the selection or octave changes while keys are held; live MIDI input and playback are not multiplied
- [ ] #5 The piano shows a marker for each extra ticked octave, and the dropdown label shows the selection
- [ ] #6 The control follows the skin and the piano row still fits at the minimum window width in every skin
- [ ] #7 Unit tests cover the octave selection and the resulting note offsets
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
