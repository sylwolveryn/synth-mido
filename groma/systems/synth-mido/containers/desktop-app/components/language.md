---
type: C4 Component
title: Language switcher
status: stable
groma:
  id: language
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/language.py
  technology: Tkinter
  group: User interface
description: Language selector; binds widget texts to keys and relabels every window
---

Widgets register their text as a key or a text function (`tr`, `bind_text`); on a language change every live binding is re-applied, including open Records and Equalizer windows, then the language-dependent lists, status bar, player bar and section titles are rebuilt. The choice is saved in the user settings.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/language.py](../../../../../../synth_mido/ui/language.py) | [synth_mido/core/i18n.py](../../../../../../synth_mido/core/i18n.py) | Switches and loads languages | Python call |
