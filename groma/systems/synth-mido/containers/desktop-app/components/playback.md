---
type: C4 Component
title: Playback engine
status: stable
groma:
  id: playback
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/playback.py
  group: Music core
  technology: Python
description: Schedules and plays a record with pause, seek and speed, per instrument
---

Turns a record into note spans and on/off events carrying each note's instrument (None for v1), drives them with after()-style callbacks and a clock, restarts sounding notes on resume/seek and never leaves notes hanging; repeats are cut per instrument and note. Also assigns MIDI channels to a record's instruments.
