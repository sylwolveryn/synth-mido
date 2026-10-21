---
type: C4 Component
title: Skin registry
status: stable
groma:
  id: registry
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/skins/registry.py
  group: Skins
  technology: Python
description: Registers skins with palettes, fonts, widget style tokens and header painter
---

Skin / WidgetStyle definitions and lookup (Registry pattern); the UI lists skins from here.
