---
type: C4 Component
title: Skin settings
status: stable
groma:
  id: skin-settings
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/skins/theme.py
  group: Skins
  technology: Python, JSON
description: Stores the chosen skin and variant and detects the OS appearance
---

Reads/writes `settings.json` (skin, variant and other user choices) with Synthwave dark as default, and detects light/dark mode on Windows, macOS and Linux.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/skins/theme.py](../../../../../../synth_mido/skins/theme.py) | [synth_mido/skins/catalog.py](../../../../../../synth_mido/skins/catalog.py) | Registers skins | Python call |
