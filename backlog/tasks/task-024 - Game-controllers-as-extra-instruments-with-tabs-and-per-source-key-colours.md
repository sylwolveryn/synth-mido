---
id: TASK-024
title: Game controllers as extra instruments with tabs and per-source key colours
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T23:58:00Z'
updated_date: '2026-10-22T00:12:00Z'
labels:
  - input
  - ui
  - audio
dependencies: []
priority: medium
type: feature
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Players want to jam with friends on game controllers next to the computer keyboard. Every detected game controller (USB or Bluetooth) becomes an additional instrument with its own sound; the instrument area gets tabs (Instrument 1 = keyboard/mouse, Instrument 2, 3 ... = controllers). Without a controller the second tab is still shown but disabled. To tell players apart, each source lights the piano keys in its own colour, and playback differs from live playing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Game controllers are detected at start and while running (hot-plug), without new required dependencies
- [ ] #2 The instrument area has tabs: Instrument 1 for keyboard/mouse, Instrument 2 always visible (disabled without a controller), and a further tab per extra connected controller
- [ ] #3 Each controller tab chooses its own instrument; the controller's buttons play notes, the D-pad shifts octave/key, and stick/trigger control velocity and sustain
- [ ] #4 Controller notes sound on their own MIDI channel, are recorded with their instrument and appear on the note bus
- [ ] #5 Keys are lit in a distinct colour per source: keyboard/mouse, each controller, MIDI input and playback; playback differs from live playing in every skin
- [ ] #6 Tests cover detection with a fake backend, button/axis mapping, channels, recording and the colour assignment
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. core/gamepad.py (Tk-free): Backend interface (devices, poll) with a Windows winmm backend via ctypes (joyConfigChanged/joyGetDevCapsW/joyGetPosEx, no new dependency) and a null backend elsewhere; PadState; PadMapper turning button/POV/axis changes into note on/off (12 buttons = major-scale degrees from the base note), octave (POV up/down), transpose (POV left/right), velocity (left stick Y) and sustain (triggers / Z axis); ControllerSlots keeping stable slot numbers for connected devices (max 4) with their own MIDI channel 12-15 and instrument.
2. playback: record channels shrink to 1-8,10,11 so controller channels never collide.
3. ui/controllers.py mixin: instrument area becomes a ttk.Notebook — tab 1 keyboard/mouse (existing instrument, volume, doubling), tab 2 always present (widgets disabled without a controller), further tabs appear per extra controller; per tab instrument, status, mapping hint and colour swatch; 2 s rescan (hot-plug) + 16 ms state polling while connected; notes to the output on the slot channel, per-slot sustain pedal, recorder (with instrument) and note bus (source controllerN).
4. skins/key_colors.py: distinct key colours per source (keyboard/MIDI, playback, controller 1-4) from the palette with a minimum distance; piano view keeps a per-key source stack and paints the newest; swatches in the tabs and the player bar.
5. i18n keys in 9 languages; tests (fake backend detection + hot-plug, mapping, channels, recording, colours in all skins); real-window smoke with a fake backend; docs + Groma.
<!-- SECTION:PLAN:END -->
