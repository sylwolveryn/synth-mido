---
type: C4 Component
title: Note bus
status: stable
groma:
  id: note-bus
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/events.py
  group: Music core
  technology: Python
description: Publishes every played note with its source to subscribed views (Observer)
---

Sources: user (mouse/keyboard), live MIDI input, playback and demos. Subscribers react without the sources knowing them: piano key painting, the note effect and the equalizer window.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | [synth_mido/ui/piano_view.py](../../../../../../synth_mido/ui/piano_view.py) | Notifies key painter | Observer |
| [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | [synth_mido/ui/fx_view.py](../../../../../../synth_mido/ui/fx_view.py) | Notifies note effect | Observer |
| [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | [synth_mido/ui/equalizer_window.py](../../../../../../synth_mido/ui/equalizer_window.py) | Notifies analyser | Observer |
