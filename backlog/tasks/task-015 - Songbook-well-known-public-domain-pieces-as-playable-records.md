---
id: TASK-015
title: 'Songbook: well-known public-domain pieces as playable records'
status: Done
assignee: []
created_date: '2026-10-21T20:51:00Z'
updated_date: '2026-10-21T21:19:00Z'
labels:
  - feature
  - content
dependencies: []
modified_files:
  - >-
    groma/systems/synth-mido/containers/synth-mido-build-songbook/components/build-songbook.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-build-songbook/components/songbook.md
  - groma/systems/synth-mido/containers/synth-mido-build-songbook/container.md
  - progress/README.md
  - progress/task-015-rondo-equalizer.png
  - progress/task-015-rondo-main.png
  - progress/task-015-songbook-list.png
  - progress/task-015.md
  - readme.md
  - records/Brahms Lullaby.json
  - records/Canon in D.json
  - records/Eine kleine Nachtmusik.json
  - records/Funeral March.json
  - records/Für Elise.json
  - records/Greensleeves.json
  - records/Gymnopédie No. 1.json
  - records/In the Hall of the Mountain King.json
  - records/Jingle Bells.json
  - records/Minuet in G.json
  - records/Moonlight Sonata.json
  - records/Morning Mood.json
  - records/Ode to Joy.json
  - records/Rondo alla Turca.json
  - records/The Entertainer.json
  - records/Toccata and Fugue in D minor.json
  - records/Twinkle Twinkle Little Star.json
  - records/William Tell Overture - Finale.json
  - scripts/build_songbook.py
  - synth_mido/core/songbook.py
  - tests/test_songbook.py
priority: medium
type: feature
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Give the user something to play back right away: a set of well-known pieces saved as record JSON files (records/ format from TASK-004) with proper names, e.g. Für Elise. Only public-domain music is included: modern copyrighted works such as the Imperial March (John Williams, 1980) are excluded; a public-domain march (Chopin Funeral March) is included instead. The pieces are written as compact note lists in a songbook module and generated into records/, so they can be checked and regenerated.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 At least 15 public-domain pieces are available as records with proper names (e.g. Für Elise, Ode to Joy, Turkish March, In the Hall of the Mountain King, Canon in D, Funeral March)
- [x] #2 Each record uses a fitting instrument and tempo and plays back correctly in the app
- [x] #3 No copyrighted works are included; the readme lists the pieces and composers
- [x] #4 A generator writes/updates the records from the songbook source
- [x] #5 Unit tests check every song is valid, in range, named correctly and has a sensible length
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. synth_mido/core/songbook.py: a compact notation (pitch:beats, chords, rests, bars), Song/Section with per-section tempo and parallel voices, to_record() into the recorder format. 2. Transcribe 18 public-domain pieces (melody + simple accompaniment, fitting GM instrument). 3. scripts/build_songbook.py writes records/<name>.json. 4. Tests: notation, validity, range, length, names, alignment, no copyrighted titles. 5. readme table, progress page, smoke test in the app.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Radetzky March (an example in the original AC) was replaced by Chopin's Funeral March: I could not transcribe its theme reliably enough, and a wrong melody under a famous title is worse than leaving it out. The Imperial March (John Williams 1980) is excluded as copyrighted. The alignment test found 3 rhythm errors in my transcriptions (Funeral March, Minuet, The Entertainer), now fixed. Verified: 199 unit tests green, smoke test 6/6 (all songs listed, they play with their instruments, the equalizer reacts).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Songbook: 18 public-domain pieces as playable records in records/ (Für Elise, Ode to Joy, Twinkle Twinkle, Rondo alla Turca, In the Hall of the Mountain King with accelerating sections, Canon in D, Funeral March, William Tell finale, Minuet in G, Morning Mood, Brahms Lullaby, Jingle Bells, Greensleeves, Eine kleine Nachtmusik, The Entertainer, Gymnopédie No. 1, Toccata and Fugue in D minor, Moonlight Sonata), each with a fitting instrument. Source in synth_mido/core/songbook.py using a compact notation with parallel voices and per-section tempo; regenerate with python -m scripts.build_songbook. No copyrighted works (Imperial March excluded; Radetzky swapped for Funeral March as documented). The transcriptions are simplified arrangements of the well-known themes, not full scores.
<!-- SECTION:FINAL_SUMMARY:END -->
