---
type: C4 Actor
title: Player
status: stable
groma:
  id: player
---

A person playing music on the VEVOR digital piano or, without it, on the computer: with the mouse on the on-screen 88-key piano or with the computer keyboard (two-row layout, octave shift, Space sustain). Records takes, plays back recordings and songbook pieces, and picks skins and visual effects.

## Relationships

| Source | Target | Description | Technology |
| --- | --- | --- | --- |
| [player](player.md) | [synth_mido/ui/input.py](../../synth_mido/ui/input.py) | Plays notes | computer keyboard |
| [player](player.md) | [synth_mido/ui/piano_view.py](../../synth_mido/ui/piano_view.py) | Clicks keys | mouse |
| [player](player.md) | [synth_mido/ui/theming.py](../../synth_mido/ui/theming.py) | Chooses skin | Tkinter UI |
| [player](player.md) | [synth_mido/ui/playback_view.py](../../synth_mido/ui/playback_view.py) | Plays back records | Tkinter UI |
| [player](player.md) | [synth_mido/ui/recording.py](../../synth_mido/ui/recording.py) | Records takes | Tkinter UI |
| [player](player.md) | [synth_mido/ui/equalizer_window.py](../../synth_mido/ui/equalizer_window.py) | Watches equalizer | Tkinter window |
| [player](player.md) | [vevor-digital-piano](../externals/vevor-digital-piano.md) | Plays | piano keys and pedal |
| [player](player.md) | [synth_mido/ui/language.py](../../synth_mido/ui/language.py) | Chooses language | Python call |
| [player](player.md) | [synth_mido/ui/controllers.py](../../synth_mido/ui/controllers.py) | Plays a game controller | game controller |
