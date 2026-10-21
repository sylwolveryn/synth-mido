---
type: C4 Component
title: Sustain pedal
status: stable
groma:
  id: sustain
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/sustain.py
  group: Music core
  technology: Python
description: Holds released notes until the pedal is lifted
---

Ledger of pedal state and sustained notes; works the same for every output and makes recordings store the real sounding length.
