---
type: C4 Component
title: MIDI settings
status: stable
groma:
  id: midi-settings
  parent: desktop-app
  group: Sound output and MIDI
  code:
    - scanner: python
      file: synth_mido/config.py
  technology: Python
description: MIDI channel, device name keywords, fallback synth keywords, instrument list
---

Static configuration read by the controller and the UI (General MIDI program numbers).
