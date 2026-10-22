---
type: C4 Component
title: Skin catalog
status: stable
groma:
  id: catalog
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/skins/catalog.py
  group: Skins
  technology: Python
description: Defines the 17 skins in dark and light variants
---

Synthwave, Classic and 15 themed skins: palettes, fonts, widget shapes and header painter.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/skins/catalog.py](../../../../../../synth_mido/skins/catalog.py) | [synth_mido/skins/palette.py](../../../../../../synth_mido/skins/palette.py) | Builds palettes | Python call |
| [synth_mido/skins/catalog.py](../../../../../../synth_mido/skins/catalog.py) | [synth_mido/skins/painters.py](../../../../../../synth_mido/skins/painters.py) | Assigns header painters | Python call |
| [synth_mido/skins/catalog.py](../../../../../../synth_mido/skins/catalog.py) | [synth_mido/skins/registry.py](../../../../../../synth_mido/skins/registry.py) | Registers skins | Python call |
| [synth_mido/skins/catalog.py](../../../../../../synth_mido/skins/catalog.py) | [synth_mido/fx/effects/base.py](../../../../../../synth_mido/fx/effects/base.py) | Names each skin's matching effect | Python call |
