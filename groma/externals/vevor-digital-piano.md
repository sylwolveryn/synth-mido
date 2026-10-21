---
type: C4 System
title: VEVOR digital piano
status: stable
groma:
  id: vevor-digital-piano
  technology: MIDI over USB / Bluetooth
---

The physical 88-key digital piano. Sends the notes, velocities and pedal the player plays (MIDI input) and can sound notes the app sends it (MIDI output). Optional: the app also works without it.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [vevor-digital-piano](vevor-digital-piano.md) | [synth_mido/audio/midi_controller.py](../../synth_mido/audio/midi_controller.py) | Sends played notes | MIDI input |
