---
type: C4 Component
title: MIDI controller
status: stable
groma:
  id: midi-controller
  parent: desktop-app
  group: Sound output and MIDI
  code:
    - scanner: python
      file: synth_mido/audio/midi_controller.py
  technology: mido, python-rtmidi
description: Single sound output and MIDI input facade
---

Opens the VEVOR piano ports; when no MIDI output is connected it falls back to an OS MIDI synthesizer port or the built-in tone generator. Sends notes, instrument changes, sustain (CC 64) and panic through one path.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | [vevor-digital-piano](../../../../../externals/vevor-digital-piano.md) | Sounds notes | MIDI output |
| [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | [os-midi-synthesizer](../../../../../externals/os-midi-synthesizer.md) | Falls back to | MIDI |
| [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | [synth_mido/audio/tone_synth.py](../../../../../../synth_mido/audio/tone_synth.py) | Falls back to | Python call |
| [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | [synth_mido/config.py](../../../../../../synth_mido/config.py) | Reads settings | Python call |
