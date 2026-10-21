---
type: C4 Component
title: Desktop UI shell
status: stable
groma:
  id: desktop-ui
  parent: desktop-app
  code:
    - scanner: python
      file: main.py
    - scanner: python
      file: synth_mido/ui/app.py
    - scanner: python
      file: synth_mido/ui/common.py
  group: User interface
  technology: Tkinter
description: Builds the main window and wires all parts together
---

`main.py` starts it; `PianoApp` (ui/app.py) creates the controller, player, recorder, keyboard player, pedal, note bus and effects, builds the sections, and composes the feature mixins (theming, connection, playback, piano view, input, effects, recording, records window). `ui/common.py` holds shared constants and formatters. Owns shutdown.
