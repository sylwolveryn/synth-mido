---
type: C4 Component
title: Game controllers
status: stable
groma:
  id: gamepad
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/core/gamepad.py
  technology: Python, ctypes, winmm
  group: Sound output and MIDI
description: Detects game controllers (hot-plug) and maps buttons, D-pad, stick and trigger to notes
---

Backend interface with the Windows winmm joystick API through ctypes (any HID controller over USB or Bluetooth, no extra dependency) and an empty backend elsewhere. PadMapper turns state changes into actions: 12 buttons play the major scale from the base note, the D-pad shifts octave (up/down) and key (left/right), the left stick sets velocity, the trigger (Z axis) is the sustain pedal; notes started by a button are remembered so shifts never leave notes hanging. ControllerSlots keeps a stable slot per connected controller (max 4), each with its own MIDI channel 12-15.
