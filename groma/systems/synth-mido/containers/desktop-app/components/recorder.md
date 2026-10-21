---
type: C4 Component
title: Recorder
status: stable
groma:
  id: recorder
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/recorder.py
  group: Music core
  technology: Python, JSON
description: Captures played notes with timing and stores records as JSON
---

Pairs note on/off into notes with start, duration and velocity plus the instrument; validates, saves, loads, lists and deletes record files in `records/`.
