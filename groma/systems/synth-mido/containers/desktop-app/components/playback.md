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
description: Schedules and plays a record with pause, seek and speed
---

Turns a record into note spans and on/off events, drives them with after()-style callbacks and a clock, restarts sounding notes on resume/seek and never leaves notes hanging.
