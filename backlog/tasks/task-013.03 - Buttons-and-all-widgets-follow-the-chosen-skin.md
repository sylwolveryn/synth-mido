---
id: TASK-013.03
title: Buttons and all widgets follow the chosen skin
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T20:51:00Z'
updated_date: '2026-10-21T21:08:00Z'
labels:
  - feature
  - design
dependencies:
  - TASK-013.01
modified_files:
  - groma/systems/synth-mido/components/catalog.md
  - groma/systems/synth-mido/components/painters.md
  - groma/systems/synth-mido/components/palette.md
  - groma/systems/synth-mido/components/registry.md
  - progress/README.md
  - progress/task-013-astronaut-dark.png
  - progress/task-013-gallery-dark.png
  - progress/task-013-gallery-light.png
  - progress/task-013-mathematics-light.png
  - progress/task-013-sakura-light.png
  - progress/task-013-steampunk-dark.png
  - progress/task-013.md
  - readme.md
  - synth_mido/skins/catalog.py
  - synth_mido/skins/painters.py
  - synth_mido/skins/palette.py
  - synth_mido/skins/registry.py
  - synth_mido/skins/theme.py
  - synth_mido/ui/app.py
  - synth_mido/ui/common.py
  - synth_mido/ui/fx_view.py
  - synth_mido/ui/input.py
  - synth_mido/ui/theming.py
  - tests/test_skins.py
  - tests/test_theme.py
  - tests/test_visualizer.py
parent_task_id: TASK-013
priority: high
type: feature
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Colours alone are not enough: buttons, sliders, checkbuttons, comboboxes, scrollbars, the log, dialogs, the piano keys, the visual effect and the equalizer window should all take their look from the skin: shape (padding, border width, relief), fonts, letter case of titles, and the colours of every state (hover, pressed, disabled, selected).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each skin defines widget style tokens (font family, title case, button padding/border/relief, accent per state) and every ttk widget style is built from them
- [x] #2 Hover, pressed, disabled and selected states use skin colours (no default-grey Tk state left)
- [x] #3 Dialogs (records window, save dialog), piano keys, keyboard range bar, visual effect and equalizer window use the skin
- [x] #4 Switching skins at runtime restyles every open window without restart
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Every ttk style in apply_theme is built from the palette + WidgetStyle (font, title case, padding, border width, relief, edge token, bold) with state maps for active/pressed/disabled/selected/focus. Small.TButton for crowded rows. skin_listeners hook for other windows (equalizer). Measure that rows fit in all skins.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
All widgets follow the skin: TButton/Accent.TButton (shape, border, relief, all state colours), the Small.TButton variant, TCheckbutton/Pedal, TCombobox and its popdowns, Scale, Entry, Treeview, Scrollbar, LabelFrame titles (case per skin), log, piano, range bar, visual effect floor, records window and save dialog. A skin_listeners hook lets further windows (the TASK-014 equalizer) restyle on switch. Fixed on the way: clam draws no border for flat relief (now raised with flat colours), and wide fonts overflowed the button rows (shorter labels, compact style, Constantia; all 34 looks measured to fit at 780 and 860 px). Smoke test 17/17.
<!-- SECTION:FINAL_SUMMARY:END -->
