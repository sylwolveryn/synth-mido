---
id: TASK-016
title: Curate the Groma architecture map for the package layout
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T21:46:00Z'
updated_date: '2026-10-21T21:51:00Z'
labels:
  - architecture
dependencies: []
modified_files:
  - groma/actors/player.md
  - groma/config.json
  - groma/externals/audio-device.md
  - groma/externals/os-midi-synthesizer.md
  - groma/externals/vevor-digital-piano.md
  - groma/flows/live-input-from-the-vevor-piano.md
  - groma/flows/play-a-note-from-the-computer-keyboard.md
  - groma/flows/record-and-play-back-a-take.md
  - groma/index.md
  - groma/project.md
  - groma/systems/synth-mido/components/animations.md
  - groma/systems/synth-mido/components/audio-init.md
  - groma/systems/synth-mido/components/catalog.md
  - groma/systems/synth-mido/components/diag.md
  - groma/systems/synth-mido/components/equalizer-window.md
  - groma/systems/synth-mido/components/events.md
  - groma/systems/synth-mido/components/fx-init.md
  - groma/systems/synth-mido/components/painters.md
  - groma/systems/synth-mido/components/palette.md
  - groma/systems/synth-mido/components/registry.md
  - groma/systems/synth-mido/components/scripts-init.md
  - groma/systems/synth-mido/components/spectrum.md
  - groma/systems/synth-mido/components/synth-mido-init.md
  - groma/systems/synth-mido/components/usb.md
  - groma/systems/synth-mido/containers/desktop-app/components/animations.md
  - groma/systems/synth-mido/containers/desktop-app/components/catalog.md
  - groma/systems/synth-mido/containers/desktop-app/components/connection.md
  - groma/systems/synth-mido/containers/desktop-app/components/desktop-ui.md
  - groma/systems/synth-mido/containers/desktop-app/components/doubling.md
  - >-
    groma/systems/synth-mido/containers/desktop-app/components/equalizer-window.md
  - groma/systems/synth-mido/containers/desktop-app/components/keyboard-play.md
  - groma/systems/synth-mido/containers/desktop-app/components/midi-check.md
  - >-
    groma/systems/synth-mido/containers/desktop-app/components/midi-controller.md
  - groma/systems/synth-mido/containers/desktop-app/components/midi-settings.md
  - groma/systems/synth-mido/containers/desktop-app/components/note-bus.md
  - >-
    groma/systems/synth-mido/containers/desktop-app/components/note-effect-view.md
  - groma/systems/synth-mido/containers/desktop-app/components/note-effect.md
  - groma/systems/synth-mido/containers/desktop-app/components/note-input.md
  - groma/systems/synth-mido/containers/desktop-app/components/painters.md
  - groma/systems/synth-mido/containers/desktop-app/components/palette.md
  - groma/systems/synth-mido/containers/desktop-app/components/piano-layout.md
  - groma/systems/synth-mido/containers/desktop-app/components/piano-view.md
  - groma/systems/synth-mido/containers/desktop-app/components/playback-view.md
  - groma/systems/synth-mido/containers/desktop-app/components/playback.md
  - groma/systems/synth-mido/containers/desktop-app/components/recorder.md
  - groma/systems/synth-mido/containers/desktop-app/components/recording.md
  - groma/systems/synth-mido/containers/desktop-app/components/records-window.md
  - groma/systems/synth-mido/containers/desktop-app/components/registry.md
  - groma/systems/synth-mido/containers/desktop-app/components/skin-settings.md
  - groma/systems/synth-mido/containers/desktop-app/components/songbook.md
  - groma/systems/synth-mido/containers/desktop-app/components/spectrum.md
  - groma/systems/synth-mido/containers/desktop-app/components/sustain.md
  - groma/systems/synth-mido/containers/desktop-app/components/theme.md
  - groma/systems/synth-mido/containers/desktop-app/components/theming.md
  - groma/systems/synth-mido/containers/desktop-app/components/tone-synth.md
  - groma/systems/synth-mido/containers/desktop-app/components/ui-init.md
  - groma/systems/synth-mido/containers/desktop-app/components/visualizer.md
  - groma/systems/synth-mido/containers/desktop-app/container.md
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
    groma/systems/synth-mido/containers/synth-mido-build-songbook/components/build-songbook.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-build-songbook/components/songbook.md
  - groma/systems/synth-mido/containers/synth-mido-build-songbook/container.md
  - >-
    groma/systems/synth-mido/containers/synth-mido-examples/components/examples.md
  - groma/systems/synth-mido/containers/synth-mido-examples/container.md
  - groma/systems/synth-mido/system.md
  - synth_mido/__pycache__/__init__.cpython-314.pyc
  - synth_mido/__pycache__/config.cpython-314.pyc
  - synth_mido/audio/__pycache__/__init__.cpython-314.pyc
  - synth_mido/audio/__pycache__/midi_controller.cpython-314.pyc
  - synth_mido/audio/__pycache__/tone_synth.cpython-314.pyc
  - synth_mido/core/__pycache__/__init__.cpython-314.pyc
  - synth_mido/core/__pycache__/doubling.cpython-314.pyc
  - synth_mido/core/__pycache__/events.cpython-314.pyc
  - synth_mido/core/__pycache__/keyboard_play.cpython-314.pyc
  - synth_mido/core/__pycache__/piano_layout.cpython-314.pyc
  - synth_mido/core/__pycache__/playback.cpython-314.pyc
  - synth_mido/core/__pycache__/recorder.cpython-314.pyc
  - synth_mido/core/__pycache__/sustain.cpython-314.pyc
  - synth_mido/fx/__pycache__/__init__.cpython-314.pyc
  - synth_mido/fx/__pycache__/animations.cpython-314.pyc
  - synth_mido/fx/__pycache__/spectrum.cpython-314.pyc
  - synth_mido/fx/__pycache__/visualizer.cpython-314.pyc
  - synth_mido/skins/__pycache__/__init__.cpython-314.pyc
  - synth_mido/skins/__pycache__/catalog.cpython-314.pyc
  - synth_mido/skins/__pycache__/painters.cpython-314.pyc
  - synth_mido/skins/__pycache__/palette.cpython-314.pyc
  - synth_mido/skins/__pycache__/registry.cpython-314.pyc
  - synth_mido/skins/__pycache__/theme.cpython-314.pyc
  - synth_mido/ui/__pycache__/__init__.cpython-314.pyc
  - synth_mido/ui/__pycache__/app.cpython-314.pyc
  - synth_mido/ui/__pycache__/common.cpython-314.pyc
  - synth_mido/ui/__pycache__/connection.cpython-314.pyc
  - synth_mido/ui/__pycache__/equalizer_window.cpython-314.pyc
  - synth_mido/ui/__pycache__/fx_view.cpython-314.pyc
  - synth_mido/ui/__pycache__/input.cpython-314.pyc
  - synth_mido/ui/__pycache__/piano_view.cpython-314.pyc
  - synth_mido/ui/__pycache__/playback_view.cpython-314.pyc
  - synth_mido/ui/__pycache__/recording.cpython-314.pyc
  - synth_mido/ui/__pycache__/records_window.cpython-314.pyc
  - synth_mido/ui/__pycache__/theming.cpython-314.pyc
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Exclude scripts/ and empty __init__.py in groma/config.json; detach and remove their components. 2. Combine the entry-file containers into one desktop-app container; move loose components in; fold the moved modules into their pre-refactor component IDs; rename file-shaped IDs to roles; group by domain. 3. Declare the player and the VEVOR piano, OS MIDI synth and audio device. 4. Describe the project, system, container and all components from the source. 5. Author verified relationships and 3 flows. 6. Two scans must leave the map unchanged.
<!-- SECTION:PLAN:END -->
