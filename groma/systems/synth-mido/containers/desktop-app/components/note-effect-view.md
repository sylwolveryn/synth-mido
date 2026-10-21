---
type: C4 Component
title: Note effect view
status: stable
groma:
  id: note-effect-view
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/fx_view.py
  group: Visual effects
  technology: Tkinter canvas
description: Draws the note effect above the piano and opens the equalizer
---

Subscribes to the note bus, animates at ~30 fps only while something is visible with pooled canvas items, and can be switched off (saved).

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/fx_view.py](../../../../../../synth_mido/ui/fx_view.py) | [synth_mido/fx/visualizer.py](../../../../../../synth_mido/fx/visualizer.py) | Animates notes | Python call |
| [synth_mido/ui/fx_view.py](../../../../../../synth_mido/ui/fx_view.py) | [synth_mido/ui/equalizer_window.py](../../../../../../synth_mido/ui/equalizer_window.py) | Opens equalizer | Python call |
