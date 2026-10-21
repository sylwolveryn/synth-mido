---
id: TASK-008.03
title: Octave shift and key labels for keyboard play
status: To Do
assignee: []
created_date: '2026-10-21T19:51:00Z'
labels:
  - feature
dependencies:
  - TASK-008.02
references:
  - ui.py
parent_task_id: TASK-008
priority: medium
type: feature
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A computer keyboard covers only about one and a half octaves, but the piano has 88 keys. The user needs to move the keyboard range up and down to reach the whole piano, and to see which piano keys the letter keys currently play.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Two dedicated keys (and matching buttons in the UI) shift the computer-keyboard range down and up by one octave
- [ ] #2 The range never goes outside A0-C8; at the ends the shift stops, and mapped notes beyond the edge are simply silent
- [ ] #3 The piano shows which keys the computer keyboard currently plays (highlighted range), and can show the letter label on each of those keys
- [ ] #4 The current octave or range is shown in the UI, and the default range starts around middle C (C4)
- [ ] #5 Shifting octave while keys are held does not leave hanging notes
- [ ] #6 Unit tests cover range shifting and its limits
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
