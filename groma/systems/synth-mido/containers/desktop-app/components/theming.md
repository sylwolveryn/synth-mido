---
type: C4 Component
title: Theming
status: stable
groma:
  id: theming
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/theming.py
  group: User interface
  technology: Tkinter ttk
description: Applies the chosen skin to every widget, the header and open windows
---

Builds every ttk style (shape, border, relief, fonts, all state colours) from the skin palette and widget tokens, draws the skin header scene, handles the skin / Sötét-Világos-Rendszer selectors and follows the OS appearance in System mode. Notifies other windows via skin listeners.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/theming.py](../../../../../../synth_mido/ui/theming.py) | [synth_mido/skins/registry.py](../../../../../../synth_mido/skins/registry.py) | Looks up skins | Python call |
| [synth_mido/ui/theming.py](../../../../../../synth_mido/ui/theming.py) | [synth_mido/skins/theme.py](../../../../../../synth_mido/skins/theme.py) | Saves skin choice | Python call |
| [synth_mido/ui/theming.py](../../../../../../synth_mido/ui/theming.py) | [synth_mido/core/i18n.py](../../../../../../synth_mido/core/i18n.py) | Translates section titles | Python call |
