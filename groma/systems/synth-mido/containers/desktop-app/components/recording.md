---
type: C4 Component
title: Recording
status: stable
groma:
  id: recording
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/recording.py
  group: User interface
  technology: Tkinter
description: Starts/stops a take and saves or discards it via a dialog
---

Feeds user and live-input notes to the Recorder, shows elapsed time and note count, and on stop asks for a name (default felvetel_YYYYMMDD_HHMMSS) before saving to `records/`.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/recording.py](../../../../../../synth_mido/ui/recording.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Saves takes | JSON |
