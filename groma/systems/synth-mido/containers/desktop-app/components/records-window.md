---
type: C4 Component
title: Records window
status: stable
groma:
  id: records-window
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/records_window.py
  group: User interface
  technology: Tkinter ttk.Treeview
description: Lists records and songbook pieces; plays and deletes them
---

A Treeview of `records/` (newest first, broken files marked) with play, multi-select delete and open-folder actions.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/records_window.py](../../../../../../synth_mido/ui/records_window.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Lists and deletes records | Python call |
| [synth_mido/ui/records_window.py](../../../../../../synth_mido/ui/records_window.py) | [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | Plays selected record | Python call |
