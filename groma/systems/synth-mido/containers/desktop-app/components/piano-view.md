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
description: Draws the 88-key piano, handles mouse play and lights keys in the colour of their source
---

Draws keys from the piano layout at the canvas's real height, the keyboard range bar and key letters; mouse presses go through the note input path. Its key painter subscribes to the note bus and keeps a per-key stack of sources, so a key shows the newest source's colour (keyboard/MIDI, playback, each controller) until every source releases it.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/piano_view.py](../../../../../../synth_mido/ui/piano_view.py) | [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | Plays clicked notes | Python call |
| [synth_mido/ui/piano_view.py](../../../../../../synth_mido/ui/piano_view.py) | [synth_mido/core/piano_layout.py](../../../../../../synth_mido/core/piano_layout.py) | Lays out keys | Python call |
| [synth_mido/ui/piano_view.py](../../../../../../synth_mido/ui/piano_view.py) | [synth_mido/skins/key_colors.py](../../../../../../synth_mido/skins/key_colors.py) | Colours keys by source | Python call |
