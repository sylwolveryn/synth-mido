---
type: C4 Component
title: Note effects
status: stable
groma:
  id: note-effect
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/fx/effects/base.py
    - scanner: python
      file: synth_mido/fx/effects/fire.py
    - scanner: python
      file: synth_mido/fx/effects/nature.py
    - scanner: python
      file: synth_mido/fx/effects/retro.py
  group: Visual effects
  technology: Python
description: 'Registry of note effects (Strategy): neon, flames, petals, leaves, steam, dust, bubbles, snow, stars, pixels and glyph sets'
---

Each effect is a Tk-free NoteEffect: per sounding note (voice) shapes drawn above the key while it sounds and for RELEASE seconds after, plus particles that burst on note-on and stream while held (BURST, RATE, LIFE). Effects declare their roles (z-order layers), the canvas kind per role (poly, oval, rect, ring, text) and the colours per role from the skin palette, so the view needs no per-effect code. Fourteen effects are registered: neon bars, flames, cherry petals, leaves, steam, sand dust, bubbles, snowflakes, stars, pixels and glyph sets (math, Roman numerals, music notes, compass stars). Every skin names its matching effect; voices and particles are capped per effect.
