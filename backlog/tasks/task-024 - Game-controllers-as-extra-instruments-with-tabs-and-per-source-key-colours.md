---
id: TASK-024
title: Game controllers as extra instruments with tabs and per-source key colours
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T23:58:00Z'
updated_date: '2026-10-22T00:25:00Z'
labels:
  - input
  - ui
  - audio
dependencies: []
modified_files:
  - groma/actors/player.md
  - groma/systems/synth-mido/containers/desktop-app/components/controllers.md
  - groma/systems/synth-mido/containers/desktop-app/components/gamepad.md
  - groma/systems/synth-mido/containers/desktop-app/components/key-colors.md
  - groma/systems/synth-mido/containers/desktop-app/components/piano-view.md
  - progress/README.md
  - progress/task-024-controllers.png
  - progress/task-024.md
  - readme.md
  - synth_mido/core/events.py
  - synth_mido/core/gamepad.py
  - synth_mido/core/playback.py
  - synth_mido/lang/de.json
  - synth_mido/lang/en.json
  - synth_mido/lang/es.json
  - synth_mido/lang/fi.json
  - synth_mido/lang/fr.json
  - synth_mido/lang/hu.json
  - synth_mido/lang/ja.json
  - synth_mido/lang/sv.json
  - synth_mido/lang/tlh.json
  - synth_mido/skins/key_colors.py
  - synth_mido/ui/app.py
  - synth_mido/ui/common.py
  - synth_mido/ui/controllers.py
  - synth_mido/ui/fx_view.py
  - synth_mido/ui/language.py
  - synth_mido/ui/piano_view.py
  - synth_mido/ui/playback_view.py
  - synth_mido/ui/theming.py
  - tests/fakes_pad.py
  - tests/test_gamepad.py
  - tests/test_playback.py
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
- [x] #1 Game controllers are detected at start and while running (hot-plug), without new required dependencies
- [x] #2 The instrument area has tabs: Instrument 1 for keyboard/mouse, Instrument 2 always visible (disabled without a controller), and a further tab per extra connected controller
- [x] #3 Each controller tab chooses its own instrument; the controller's buttons play notes, the D-pad shifts octave/key, and stick/trigger control velocity and sustain
- [x] #4 Controller notes sound on their own MIDI channel, are recorded with their instrument and appear on the note bus
- [x] #5 Keys are lit in a distinct colour per source: keyboard/mouse, each controller, MIDI input and playback; playback differs from live playing in every skin
- [x] #6 Tests cover detection with a fake backend, button/axis mapping, channels, recording and the colour assignment
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
No game controller is attached to the development machine, so the winmm backend was only verified to load and return an empty list; all behaviour was tested through a fake backend. Controllers do not send CC64; their sustain defers note-offs (works on every output). Record playback channels reduced to 1-8,10,11 so controller channels 12-15 never collide. Also fixed a layout bug present since TASK-022: at 780x800 the listen section (Record/Recordings/Equalizer) was pushed off-screen; earlier fit checks read stale heights. The listen section is now packed first, the piano section uses grid weights so the effect band and keys shrink proportionally, and keys/effects draw at the canvas's real height. Log minimum height lowered to 2 lines.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Every detected game controller (winmm via ctypes, USB/Bluetooth, hot-plug, no new dependency) becomes an extra instrument: the instrument area is now tabbed (1 keyboard/mouse, 2 always visible and disabled without a controller, more tabs per connected controller), each tab picks its own instrument and plays on its own MIDI channel. Buttons play a major scale, the D-pad shifts octave and key, the stick sets velocity and the trigger is a per-controller sustain pedal; notes are recorded with their instrument and published on the note bus. Keys are lit in a distinct, visible colour per source (keyboard/MIDI, playback, each controller) in all 34 looks, with a per-key source stack. Also fixed the minimum-size layout so the record controls are always visible. Verified by 19 unit tests with a fake backend and a real-window smoke test (24/24); not verified with physical controller hardware.
<!-- SECTION:FINAL_SUMMARY:END -->
