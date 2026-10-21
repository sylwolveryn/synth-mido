---
type: C4 Container
title: Desktop app
status: stable
groma:
  id: desktop-app
  parent: synth-mido
  technology: Python 3, Tkinter/ttk, mido
description: 'Tkinter application: UI, music logic, MIDI/audio output, skins and effects'
---

Started by `main.py`. Tk-free models in `synth_mido/core` and `synth_mido/fx` hold the music and effect logic; `synth_mido/ui` is a thin Tk view layer composed into one `PianoApp`. Every played note is published on the note bus (Observer), which the piano view, the note effect and the equalizer window subscribe to. All visible texts come from key-value language files in `synth_mido/lang/` (Hungarian reference plus eight translations). Data: record JSON files in `records/` (format version 2: one instrument per note) and per-user settings in `%APPDATA%/synth-mido/settings.json` (or `~/.config/synth-mido`).
