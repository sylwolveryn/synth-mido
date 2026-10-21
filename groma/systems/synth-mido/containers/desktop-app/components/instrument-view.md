---
type: C4 Component
title: Instrument illustration view
status: stable
groma:
  id: instrument-view
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/instrument_view.py
  technology: Tkinter canvas
  group: User interface
description: Shows the selected instrument's illustration and caption
---

A canvas in the Playback section next to Open / Stop, redrawn when the instrument, the skin, the language or the window size changes (also when a version 1 record sets the instrument).

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/instrument_view.py](../../../../../../synth_mido/ui/instrument_view.py) | [synth_mido/fx/instrument_art.py](../../../../../../synth_mido/fx/instrument_art.py) | Draws the illustration | Tk canvas |
