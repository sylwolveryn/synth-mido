---
id: TASK-015
title: 'Songbook: well-known public-domain pieces as playable records'
status: To Do
assignee: []
created_date: '2026-10-21T20:51:00Z'
updated_date: '2026-10-21T21:18:00Z'
labels:
  - feature
  - content
dependencies: []
priority: medium
type: feature
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Give the user something to play back right away: a set of well-known pieces saved as record JSON files (records/ format from TASK-004) with proper names, e.g. Für Elise. Only public-domain music is included: modern copyrighted works such as the Imperial March (John Williams, 1980) are excluded; public-domain marches (Radetzky March, Chopin Funeral March) are included instead. The pieces are written as compact note lists in a songbook module and generated into records/, so they can be checked and regenerated.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 At least 15 public-domain pieces are available as records with proper names (e.g. Für Elise, Ode to Joy, Turkish March, In the Hall of the Mountain King, Canon in D, Funeral March)
- [ ] #2 Each record uses a fitting instrument and tempo and plays back correctly in the app
- [ ] #3 No copyrighted works are included; the readme lists the pieces and composers
- [ ] #4 A generator writes/updates the records from the songbook source
- [ ] #5 Unit tests check every song is valid, in range, named correctly and has a sensible length
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
