---
type: C4 Component
title: MIDI connection
status: stable
groma:
  id: connection
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/connection.py
  group: User interface
  technology: Tkinter, mido
description: Lists devices, connects input/output, picks the instrument and polls live input
---

Opens ports through the MIDI controller, shows the active output (device or fallback) in the status bar, applies the selected instrument and, while listening, polls the MIDI input every 15 ms and publishes incoming notes on the note bus and to a running recording.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/connection.py](../../../../../../synth_mido/ui/connection.py) | [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | Connects and polls | Python call |
| [synth_mido/ui/connection.py](../../../../../../synth_mido/ui/connection.py) | [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | Publishes live notes | Python call |
| [synth_mido/ui/connection.py](../../../../../../synth_mido/ui/connection.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Records live notes | Python call |
