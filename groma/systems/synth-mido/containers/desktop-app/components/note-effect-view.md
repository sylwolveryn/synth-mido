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
description: Draws the selected effect above the piano with pooled canvas items; effect selector and auto-switch on skin change
---

Subscribes to the note bus and animates at ~30 fps only while something is visible. Renders any registered effect generically: canvas items are pooled per role, layer order is restored only when new items appear, text glyph fonts are pre-loaded off-screen. The effect follows the skin's matching effect on every skin change, can be chosen by hand in the selector next to the appearance, and the choice is saved; Effekt switches it off.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/fx_view.py](../../../../../../synth_mido/ui/fx_view.py) | [synth_mido/fx/visualizer.py](../../../../../../synth_mido/fx/visualizer.py) | Animates notes | Python call |
| [synth_mido/ui/fx_view.py](../../../../../../synth_mido/ui/fx_view.py) | [synth_mido/ui/equalizer_window.py](../../../../../../synth_mido/ui/equalizer_window.py) | Opens equalizer | Python call |
