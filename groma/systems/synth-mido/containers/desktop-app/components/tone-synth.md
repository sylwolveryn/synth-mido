---
type: C4 Component
title: Tone generator
status: stable
groma:
  id: tone-synth
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/audio/tone_synth.py
  group: Sound output and MIDI
  technology: numpy, sounddevice
description: Built-in fallback synthesizer for computers without a MIDI synth
---

Mixes decaying sine voices for note on/off into the default audio device; behaves like a MIDI output port.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/audio/tone_synth.py](../../../../../../synth_mido/audio/tone_synth.py) | [audio-device](../../../../../externals/audio-device.md) | Plays waveform | PortAudio |
