---
type: C4 Component
title: Equalizer window
status: stable
groma:
  id: equalizer-window
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/equalizer_window.py
  group: Visual effects
  technology: Tkinter
description: Separate Winamp-style analyser window with selectable animations
---

Subscribes to the note bus, animates while open and active, restyles on skin change and remembers the chosen animation.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/equalizer_window.py](../../../../../../synth_mido/ui/equalizer_window.py) | [synth_mido/fx/spectrum.py](../../../../../../synth_mido/fx/spectrum.py) | Feeds notes | Python call |
| [synth_mido/ui/equalizer_window.py](../../../../../../synth_mido/ui/equalizer_window.py) | [synth_mido/fx/animations.py](../../../../../../synth_mido/fx/animations.py) | Renders frames | Python call |
