---
type: C4 Component
title: Controller instruments view
status: stable
groma:
  id: controllers
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/controllers.py
  technology: Tkinter ttk
  group: User interface
description: 'Instrument tabs: 1 keyboard/mouse, 2+ one per game controller'
---

Turns the instrument area into a notebook. Instrument 2 is always shown (disabled without a controller); further tabs appear and disappear with hot-plug. Rescans every 2 s and polls connected controllers every 16 ms; each tab chooses its own instrument, and controller notes go to the output on the slot's channel, a per-slot sustain pedal, the recorder (with the instrument) and the note bus as source controllerN. Shows each source's key colour as a swatch.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/controllers.py](../../../../../../synth_mido/ui/controllers.py) | [synth_mido/core/gamepad.py](../../../../../../synth_mido/core/gamepad.py) | Detects and polls controllers | Python call |
| [synth_mido/ui/controllers.py](../../../../../../synth_mido/ui/controllers.py) | [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | Sounds controller notes | MIDI channel 12-15 |
| [synth_mido/ui/controllers.py](../../../../../../synth_mido/ui/controllers.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Records controller notes | Python call |
| [synth_mido/ui/controllers.py](../../../../../../synth_mido/ui/controllers.py) | [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | Publishes controller notes | Python call |
| [synth_mido/ui/controllers.py](../../../../../../synth_mido/ui/controllers.py) | [synth_mido/skins/key_colors.py](../../../../../../synth_mido/skins/key_colors.py) | Shows source colour swatches | Python call |
