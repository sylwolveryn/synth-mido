---
type: C4 Component
title: Songbook
status: stable
groma:
  id: songbook
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/songbook.py
  group: Music core
  technology: Python
description: Public-domain pieces written in a compact notation and turned into records
---

18 pieces (Für Elise, Canon in D, ...) as sections with tempo and parallel voices; `to_record()` produces the record JSON. Regenerated into `records/` by a development script.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/core/songbook.py](../../../../../../synth_mido/core/songbook.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Builds records | Python call |
