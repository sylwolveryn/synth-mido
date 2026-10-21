---
type: Groma Flow
title: Live input from the VEVOR piano
groma:
  id: live-input-from-the-vevor-piano
---

Notes played on the physical piano arrive as MIDI input, are polled by the connection view and published, so the key lights up and the equalizer reacts.

## Steps

| From | To | Action |
| --- | --- | --- |
| [Player](../actors/player.md) | [VEVOR digital piano](../externals/vevor-digital-piano.md) | Play on the piano |
| [VEVOR digital piano](../externals/vevor-digital-piano.md) | [MIDI controller](../systems/synth-mido/containers/desktop-app/components/midi-controller.md) | Send MIDI notes |
| [MIDI connection](../systems/synth-mido/containers/desktop-app/components/connection.md) | [MIDI controller](../systems/synth-mido/containers/desktop-app/components/midi-controller.md) | Poll the input |
| [MIDI connection](../systems/synth-mido/containers/desktop-app/components/connection.md) | [Note bus](../systems/synth-mido/containers/desktop-app/components/note-bus.md) | Publish live notes |
| [Note bus](../systems/synth-mido/containers/desktop-app/components/note-bus.md) | [Piano view](../systems/synth-mido/containers/desktop-app/components/piano-view.md) | Light the key |
| [Note bus](../systems/synth-mido/containers/desktop-app/components/note-bus.md) | [Equalizer window](../systems/synth-mido/containers/desktop-app/components/equalizer-window.md) | Update the spectrum |
