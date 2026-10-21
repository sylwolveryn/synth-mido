---
id: TASK-016
title: Curate the Groma architecture map for the package layout
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T21:46:00Z'
labels:
  - architecture
dependencies: []
priority: medium
type: docs
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After the TASK-012 refactor the Groma map is still an uncurated first scan: the one desktop application appears as several containers named after entry files, pre-refactor components without code sit next to their moved twins, empty __init__.py files and hardware/diagnostic scripts appear as product components, and nothing is described. A new reader cannot see who uses the app, what its parts do or how they work together.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dev tooling (scripts/, tests, empty __init__ files) is excluded from the architecture
- [ ] #2 The desktop application is one container whose components match the real responsibilities, grouped by domain
- [ ] #3 The player, the VEVOR piano, the OS MIDI synthesizer and the audio device are declared as actor / external systems
- [ ] #4 System, container and every component have a description and overview based on the source
- [ ] #5 Relationships and at least two flows explain the main scenarios (playing a note, recording and playback)
- [ ] #6 Two consecutive groma scans leave the curated map unchanged
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
