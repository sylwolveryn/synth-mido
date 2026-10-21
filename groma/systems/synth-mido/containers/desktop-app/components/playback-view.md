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
description: Opening records and the player bar; v2 records play each instrument on its own channel
---

Open… and Stop (player, pedal and all notes), plus the player bar (play/pause, stop, seek slider, speed). A version 2 record gets one MIDI channel per instrument (1-15, drum channel 9 skipped) so it plays several instruments at once while the user keeps channel 0; a version 1 record plays on the main channel with the selected, overridable instrument. Played-back notes go to the output, the note bus and a running recording.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/core/playback.py](../../../../../../synth_mido/core/playback.py) | Drives player | Python call |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/audio/midi_controller.py](../../../../../../synth_mido/audio/midi_controller.py) | Sounds notes | Python call |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/core/events.py](../../../../../../synth_mido/core/events.py) | Publishes notes | Python call |
| [synth_mido/ui/playback_view.py](../../../../../../synth_mido/ui/playback_view.py) | [synth_mido/core/recorder.py](../../../../../../synth_mido/core/recorder.py) | Feeds played-back notes into a take | Python call |
