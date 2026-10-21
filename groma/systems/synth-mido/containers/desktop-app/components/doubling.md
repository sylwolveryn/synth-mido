---
type: C4 Component
title: Octave doubling
status: stable
groma:
  id: doubling
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/doubling.py
  group: Music core
  technology: Python
description: Adds the same note one octave up and/or down for two-hand playing
---

Off / +1 / -1 / both; remembers which real notes each key started and reference-counts shared notes so nothing hangs when the setting or octave changes.
