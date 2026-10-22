---
type: C4 Component
title: Key colours per source
status: stable
groma:
  id: key-colors
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/skins/key_colors.py
  technology: Python
  group: Skins
description: Distinct key highlight colours for keyboard/MIDI, playback and each controller
---

Derived from the skin palette plus a vivid fallback list so that every source differs from the others and from the unlit key colours by a minimum RGB distance in all 34 looks; playback always differs from live playing.
