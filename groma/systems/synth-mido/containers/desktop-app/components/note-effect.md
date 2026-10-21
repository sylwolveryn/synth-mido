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
description: Rising neon bars, trails and sparks for played notes
---

Tk-free model with capped bars and sparks; returns shapes per frame.
