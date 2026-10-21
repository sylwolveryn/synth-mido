---
type: C4 Component
title: Note input
status: stable
groma:
  id: note-input
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/input.py
  group: User interface
  technology: Tkinter
description: 'The path of user-played notes: computer keyboard, sustain pedal, octave doubling'
---

Binds key events, filters text fields, routes mouse and keyboard notes through octave doubling and the sustain pedal, then to the output, the recorder and the note bus. Space acts as the pedal.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | [synth_mido/core/keyboard_play.py](../../../../../../synth_mido/core/keyboard_play.py) | Maps keys | Python call |
| [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | [synth_mido/core/doubling.py](../../../../../../synth_mido/core/doubling.py) | Doubles notes | Python call |
| [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | [synth_mido/core/sustain.py](../../../../../../synth_mido/core/sustain.py) | Holds notes | Python call |
| [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | Sounds notes | Python call |
| [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Records notes | Python call |
| [synth_mido/ui/input.py](../../../../../../synth_mido/ui/input.py) | [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | Publishes notes | Python call |
