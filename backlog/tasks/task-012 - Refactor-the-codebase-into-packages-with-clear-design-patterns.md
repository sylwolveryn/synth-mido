---
id: TASK-012
title: Refactor the codebase into packages with clear design patterns
status: To Do
assignee: []
created_date: '2026-10-21T20:50:00Z'
labels:
  - refactor
dependencies: []
priority: high
type: chore
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
All modules sit flat in the repository root and ui.py has grown to ~1400 lines that mix layout, theming, playback, recording, keyboard handling, effects and dialogs. Every new feature (skins, equalizer window, songbook) makes this harder to change safely. The code should be organised into packages by responsibility, with a few well-known patterns where they remove real coupling: an Observer note bus so the piano view, visual effects and the coming equalizer window subscribe to played notes instead of being called from highlight(); Strategy + Registry for skins/header painters and equalizer animations; models kept free of Tk so they stay unit-testable. Behaviour must not change.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Source code lives in a synth_mido package with sub-packages by responsibility (core models, audio/MIDI, skins/theme, fx, ui); main.py is the only app entry point in the root
- [ ] #2 Unit tests live in a tests/ folder; hardware/diagnostic scripts (test_midi, diag, examples, usb) live in scripts/
- [ ] #3 The main window is split into focused modules instead of one ~1400 line ui.py
- [ ] #4 A NoteBus (Observer) publishes every played note with its source; the piano highlight and the visual effect subscribe to it
- [ ] #5 All features behave as before (verified by the full unit suite and the existing smoke scenarios)
- [ ] #6 pre-commit, readme and Groma architecture reflect the new layout
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
