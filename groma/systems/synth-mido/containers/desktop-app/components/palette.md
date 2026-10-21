---
type: C4 Component
title: Palette builder
status: stable
groma:
  id: palette
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/skins/palette.py
  group: Skins
  technology: Python
description: Derives a full colour palette from a few base colours with readable contrast
---

Builds the 25 colour tokens of a skin variant and nudges text colours until every text/background pair reaches WCAG 4.5:1.
