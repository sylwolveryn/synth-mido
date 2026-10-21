---
type: C4 Component
title: Header painters
status: stable
groma:
  id: painters
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/skins/painters.py
  group: Skins
  technology: Tkinter canvas
description: Draws each skin's header scene on a canvas (Strategy)
---

One painter per skin (sunset grid, planets, gears, pixel invaders, ...) using only canvas primitives, scaled to the window width.
