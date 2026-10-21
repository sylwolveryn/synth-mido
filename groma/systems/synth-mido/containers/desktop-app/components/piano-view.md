---
type: C4 Component
title: Piano view
status: stable
groma:
  id: piano-view
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/piano_view.py
  group: User interface
  technology: Tkinter canvas
description: Draws the 88-key piano, handles mouse play and lights keys from the note bus
---

Draws keys from the piano layout, the keyboard range bar and key letters; mouse presses go through the note input path. Its key painter subscribes to the note bus, so every note source lights the right key.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/piano_view.py](../../../../../../synth_mido/ui/piano_view.py) | [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | Plays clicked notes | Python call |
| [synth_mido/ui/piano_view.py](../../../../../../synth_mido/ui/piano_view.py) | [synth_mido/core/piano_layout.py](../../../../../../synth_mido/core/piano_layout.py) | Lays out keys | Python call |
