---
type: Groma Flow
title: Record and play back a take
groma:
  id: record-and-play-back-a-take
---

The player records a take, saves it as JSON, then opens it in the player bar, which schedules the notes and sends them to the output and the note bus.

## Steps

| From | To | Action |
| --- | --- | --- |
| [Player](../actors/player.md) | [Recording](../systems/synth-mido/containers/desktop-app/components/recording.md) | Start recording |
| [Player](../actors/player.md) | [Note input](../systems/synth-mido/containers/desktop-app/components/note-input.md) | Play notes |
| [Note input](../systems/synth-mido/containers/desktop-app/components/note-input.md) | [Recorder](../systems/synth-mido/containers/desktop-app/components/recorder.md) | Capture each note |
| [Recording](../systems/synth-mido/containers/desktop-app/components/recording.md) | [Recorder](../systems/synth-mido/containers/desktop-app/components/recorder.md) | Save the take as JSON |
| [Player](../actors/player.md) | [Playback view](../systems/synth-mido/containers/desktop-app/components/playback-view.md) | Open the record |
| [Playback view](../systems/synth-mido/containers/desktop-app/components/playback-view.md) | [Recorder](../systems/synth-mido/containers/desktop-app/components/recorder.md) | Load the JSON |
| [Playback view](../systems/synth-mido/containers/desktop-app/components/playback-view.md) | [Player](../systems/synth-mido/containers/desktop-app/components/playback.md) | Schedule and play |
| [Playback view](../systems/synth-mido/containers/desktop-app/components/playback-view.md) | [MIDI controller](../systems/synth-mido/containers/desktop-app/components/midi-controller.md) | Sound the notes |
| [Playback view](../systems/synth-mido/containers/desktop-app/components/playback-view.md) | [Note bus](../systems/synth-mido/containers/desktop-app/components/note-bus.md) | Publish the notes |
