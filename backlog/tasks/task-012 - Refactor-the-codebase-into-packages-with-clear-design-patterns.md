---
id: TASK-012
title: Refactor the codebase into packages with clear design patterns
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T20:50:00Z'
updated_date: '2026-10-21T20:56:00Z'
labels:
  - refactor
dependencies: []
modified_files:
  - .pre-commit-config.yaml
  - groma/systems/synth-mido/components/audio-init.md
  - groma/systems/synth-mido/components/diag.md
  - groma/systems/synth-mido/components/events.md
  - groma/systems/synth-mido/components/fx-init.md
  - groma/systems/synth-mido/components/scripts-init.md
  - groma/systems/synth-mido/components/synth-mido-init.md
  - groma/systems/synth-mido/components/usb.md
  - groma/systems/synth-mido/containers/desktop-app/components/desktop-ui.md
  - groma/systems/synth-mido/containers/desktop-app/components/doubling.md
  - groma/systems/synth-mido/containers/desktop-app/components/keyboard-play.md
  - groma/systems/synth-mido/containers/desktop-app/components/midi-check.md
  - >-
    groma/systems/synth-mido/containers/desktop-app/components/midi-controller.md
  - groma/systems/synth-mido/containers/desktop-app/components/midi-settings.md
  - groma/systems/synth-mido/containers/desktop-app/components/piano-layout.md
  - groma/systems/synth-mido/containers/desktop-app/components/playback.md
  - groma/systems/synth-mido/containers/desktop-app/components/recorder.md
  - groma/systems/synth-mido/containers/desktop-app/components/sustain.md
  - groma/systems/synth-mido/containers/desktop-app/components/theme.md
  - groma/systems/synth-mido/containers/desktop-app/components/tone-synth.md
  - groma/systems/synth-mido/containers/desktop-app/components/ui-init.md
  - groma/systems/synth-mido/containers/desktop-app/components/visualizer.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/app.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/audio-midi-controller.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/audio-tone-synth.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/common.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/connection.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/core-doubling.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/core-init.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/core-keyboard-play.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/core-piano-layout.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/core-playback.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/core-recorder.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/core-sustain.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/fx-view.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/fx-visualizer.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/input.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/piano-view.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/playback-view.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/recording.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/records-window.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/skins-init.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/skins-theme.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-app/components/synth-mido-config.md
  - groma/systems/synth-mido/containers/synth-mido-app/components/theming.md
  - groma/systems/synth-mido/containers/synth-mido-app/container.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-examples/components/examples.md
  - groma/systems/synth-mido/containers/synth-mido-examples/container.md
  - main.py
  - progress/README.md
  - progress/task-012.md
  - readme.md
  - scripts/__init__.py
  - scripts/diag.py
  - scripts/examples.py
  - scripts/midi_check.py
  - scripts/usb.py
  - synth_mido/__init__.py
  - synth_mido/audio/__init__.py
  - synth_mido/audio/midi_controller.py
  - synth_mido/audio/tone_synth.py
  - synth_mido/config.py
  - synth_mido/core/__init__.py
  - synth_mido/core/doubling.py
  - synth_mido/core/events.py
  - synth_mido/core/keyboard_play.py
  - synth_mido/core/piano_layout.py
  - synth_mido/core/playback.py
  - synth_mido/core/recorder.py
  - synth_mido/core/sustain.py
  - synth_mido/fx/__init__.py
  - synth_mido/fx/visualizer.py
  - synth_mido/skins/__init__.py
  - synth_mido/skins/theme.py
  - synth_mido/ui/__init__.py
  - synth_mido/ui/app.py
  - synth_mido/ui/common.py
  - synth_mido/ui/connection.py
  - synth_mido/ui/fx_view.py
  - synth_mido/ui/input.py
  - synth_mido/ui/piano_view.py
  - synth_mido/ui/playback_view.py
  - synth_mido/ui/recording.py
  - synth_mido/ui/records_window.py
  - synth_mido/ui/theming.py
  - tests/__init__.py
  - tests/fakes.py
  - tests/test_audio_output.py
  - tests/test_doubling.py
  - tests/test_events.py
  - tests/test_keyboard_play.py
  - tests/test_piano_layout.py
  - tests/test_playback.py
  - tests/test_recorder.py
  - tests/test_sustain.py
  - tests/test_theme.py
  - tests/test_visualizer.py
  - ui.py
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
- [x] #1 Source code lives in a synth_mido package with sub-packages by responsibility (core models, audio/MIDI, skins/theme, fx, ui); main.py is the only app entry point in the root
- [x] #2 Unit tests live in a tests/ folder; hardware/diagnostic scripts (test_midi, diag, examples, usb) live in scripts/
- [x] #3 The main window is split into focused modules instead of one ~1400 line ui.py
- [x] #4 A NoteBus (Observer) publishes every played note with its source; the piano highlight and the visual effect subscribe to it
- [x] #5 All features behave as before (verified by the full unit suite and the existing smoke scenarios)
- [x] #6 pre-commit, readme and Groma architecture reflect the new layout
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. git mv modules into synth_mido/{core,audio,skins,fx,ui}, tests into tests/, hardware scripts into scripts/. 2. Scripted import rewrite. 3. Split ui.py into an app.py composition plus 8 mixin modules and common.py (AST-based, behaviour preserving). 4. Add a NoteBus (Observer) in core/events.py; the piano highlight and visual effect subscribe, and call sites tag the source. 5. tests/fakes.py for shared fakes; pre-commit uses unittest discover. 6. readme structure section, groma scan, progress page.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified: 163 unit tests green via discover (159 existing + 4 NoteBus), ruff clean, pre-commit --all-files green. All 11 earlier real-window smoke scripts were rerun on the new layout through module aliases, with results identical to the pre-refactor run (the only failures are the previously explained obsolete expectations). groma scan refreshed 34 components for the moved files.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The codebase now lives in a synth_mido package: core/ (Tk-free models plus the new events.NoteBus), audio/ (MIDI facade and tone synth), skins/ (theme), fx/ (visualizer), ui/ (app.py composition plus theming, connection, playback_view, piano_view, input, fx_view, recording and records_window mixins, and common.py). Tests moved to tests/ with shared fakes, hardware scripts to scripts/; main.py is the only root entry point. NoteBus (Observer) publishes every note with its source; key painting and the visual effect subscribe. Behaviour is unchanged; files were moved with git mv to keep history.
<!-- SECTION:FINAL_SUMMARY:END -->
