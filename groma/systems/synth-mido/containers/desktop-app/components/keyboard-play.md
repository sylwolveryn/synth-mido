---
type: C4 Component
title: Keyboard player
status: stable
groma:
  id: keyboard-play
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/keyboard_play.py
  group: Music core
  technology: Python
description: Maps computer keys to notes with auto-repeat filtering and octave shift
---

Two-row QWERTZ/QWERTY layout (18 notes), X/C octave shift across A0-C8, Space pedal key, deferred releases that hide OS auto-repeat.
