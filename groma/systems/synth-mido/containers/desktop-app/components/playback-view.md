---
type: C4 Component
title: Playback view
status: stable
groma:
  id: playback-view
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/ui/playback_view.py
  group: User interface
  technology: Tkinter
description: Demo buttons and the player bar for recordings
---

Scale/chord/demo sequences, opening a record file, and the player bar (play/pause, stop, seek slider, speed). Drives the Player model and sends its notes to the output and the note bus; only one thing plays at a time.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Loads records | JSON |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/core/playback.py](../../../../../../synth_mido/core/playback.py) | Drives player | Python call |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | Sounds notes | Python call |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | Publishes notes | Python call |
