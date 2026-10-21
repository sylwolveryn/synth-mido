---
type: Groma Flow
title: Play a note from the computer keyboard
groma:
  id: play-a-note-from-the-computer-keyboard
---

Without a MIDI piano: a key press becomes a note (with optional octave doubles), sounds on the fallback synthesizer and is published so the piano key lights up and a neon bar rises.

## Steps

| From | To | Action |
| --- | --- | --- |
| [Player](../actors/player.md) | [Note input](../systems/synth-mido/containers/desktop-app/components/note-input.md) | Press a letter key |
| [Note input](../systems/synth-mido/containers/desktop-app/components/note-input.md) | [Keyboard player](../systems/synth-mido/containers/desktop-app/components/keyboard-play.md) | Map the key to a note |
| [Note input](../systems/synth-mido/containers/desktop-app/components/note-input.md) | [Octave doubling](../systems/synth-mido/containers/desktop-app/components/doubling.md) | Add octave doubles |
| [Note input](../systems/synth-mido/containers/desktop-app/components/note-input.md) | [MIDI controller](../systems/synth-mido/containers/desktop-app/components/midi-controller.md) | Send note on |
| [MIDI controller](../systems/synth-mido/containers/desktop-app/components/midi-controller.md) | [OS MIDI synthesizer](../externals/os-midi-synthesizer.md) | Sound it on the fallback synth |
| [Note input](../systems/synth-mido/containers/desktop-app/components/note-input.md) | [Note bus](../systems/synth-mido/containers/desktop-app/components/note-bus.md) | Publish the note |
| [Note bus](../systems/synth-mido/containers/desktop-app/components/note-bus.md) | [Piano view](../systems/synth-mido/containers/desktop-app/components/piano-view.md) | Light the key |
| [Note bus](../systems/synth-mido/containers/desktop-app/components/note-bus.md) | [Note effect view](../systems/synth-mido/containers/desktop-app/components/note-effect-view.md) | Spawn a neon bar |
