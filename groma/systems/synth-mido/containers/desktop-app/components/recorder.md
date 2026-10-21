---
type: C4 Component
title: Recorder
status: stable
groma:
  id: recorder
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/recorder.py
  group: Music core
  technology: Python, JSON
description: 'Captures everything that sounds and stores records as JSON (format v2: instrument per note)'
---

Pairs note on/off per (instrument, note) into notes with start, duration, velocity and instrument; user, live-input and played-back notes mesh into one take, and an instrument change mid-take applies to later notes. Validates v1 (single overridable instrument: old takes, songbook) and v2; saves, loads, lists and deletes record files in `records/`.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | [synth_mido/core/i18n.py](../../../../../../synth_mido/core/i18n.py) | Translates validation errors | Python call |
