---
type: C4 Component
title: Note effect model
status: stable
groma:
  id: note-effect
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/fx/visualizer.py
  group: Visual effects
  technology: Python
description: Glowing flames with rising embers for played notes
---

Tk-free model: per sounding note a three-layer halo, a flickering smoothed flame and a bright core whose height and brightness follow velocity; embers burst on note-on and rise while held; flames die down after release. Capped at 40 flames and 70 embers; returns layered shapes.
