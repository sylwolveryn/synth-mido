---
id: TASK-014
title: Winamp-style equalizer window with selectable animations
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T20:51:00Z'
updated_date: '2026-10-21T21:13:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-012
modified_files:
  - groma/systems/synth-mido/components/animations.md
  - groma/systems/synth-mido/components/equalizer-window.md
  - groma/systems/synth-mido/components/spectrum.md
  - progress/README.md
  - progress/task-014-equalizer.png
  - progress/task-014.md
  - readme.md
  - synth_mido/fx/animations.py
  - synth_mido/fx/spectrum.py
  - synth_mido/ui/app.py
  - synth_mido/ui/equalizer_window.py
  - synth_mido/ui/fx_view.py
  - tests/test_equalizer.py
priority: medium
type: feature
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The user wants the classic Winamp visualisation feeling: a separate window with a spectrum analyser and other animated effects that react to the music, with a selector to switch between styles. The app has no audio stream to run an FFT on, so the analyser is driven by the notes being played (each note feeds the frequency band of its pitch, with attack, decay and falling peak caps), which works for every note source and every output.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A button in the main window opens a separate, resizable equalizer window (opening it again focuses the existing one)
- [ ] #2 At least 5 selectable animations: classic bars with falling peak caps, mirrored bars, oscilloscope line, circular radial bars and a fire/plasma style
- [ ] #3 It reacts to every note source via the NoteBus (mouse, keyboard, live MIDI input, playback, demos), with band level from velocity and smooth decay
- [ ] #4 Colours follow the current skin and update on skin change
- [ ] #5 Animation runs at ~30 fps only while the window is open, with bounded per-frame cost
- [ ] #6 The chosen animation is remembered between runs
- [ ] #7 Unit tests cover the spectrum model (bands, decay, peak caps) and each animation strategy without a real window
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. fx/spectrum.py: a Tk-free Spectrum fed by notes (band per pitch, neighbour and octave contributions, summed for chords, attack/decay/peak hold+fall, wave samples). 2. fx/animations.py: Animation strategies + registry (bars with LED grille, mirror, scope, radial, fire, area) returning role-tagged shapes. 3. ui/equalizer_window.py: Toplevel with an animation combobox; subscribes to the NoteBus, pooled canvas items, skin colours via skin_listeners, runs only while open and active; choice saved. 4. Equalizer… button; tests and smoke test with screenshots.
<!-- SECTION:PLAN:END -->
