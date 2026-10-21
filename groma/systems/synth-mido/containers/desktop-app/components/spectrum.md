---
type: C4 Component
title: Spectrum model
status: stable
groma:
  id: spectrum
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/fx/spectrum.py
  group: Visual effects
  technology: Python
description: Note-driven 24-band spectrum with attack, decay and falling peaks
---

No audio stream is available for an FFT, so notes feed the band of their pitch (plus overtone spill); also produces an oscilloscope waveform.
