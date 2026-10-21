---
type: C4 Component
title: Piano layout
status: stable
groma:
  id: piano-layout
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/piano_layout.py
  group: Music core
  technology: Python
description: Geometry of the 88-key keyboard (A0-C8)
---

Key rectangles for any width, black/white pattern, labels and hit testing; shared by the piano view, the note effect and the octave range bar.
