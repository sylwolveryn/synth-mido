---
id: TASK-003
title: >-
  add some cool Design to the UI, with dark, light and like OS system (also: as
  default) theme
status: Done
assignee: []
created_date: '2026-10-21T15:59:00Z'
updated_date: '2026-10-21T16:48:00Z'
labels:
  - ui theme
dependencies: []
references:
  - ui.py
priority: medium
type: feature
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Tkinter window in ui.py still uses default ttk/vista styling plus hardcoded piano and canvas colors. There is no Light, Dark, or System appearance, so the app cannot match the OS on first launch or let the user pick a look. This parent tracks a themed UI that stays readable across ttk widgets, the canvas piano, and the MIDI log, without changing MIDI behavior.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Scope: styling only in ui.py plus a new theme.py. Connect, play and listen code paths are not touched. UI labels are Hungarian. Settings live in the user config dir.

Current state: all UI is in ui.py (PianoApp). run() hardcodes ttk theme "vista" (Windows only, cannot be recolored). Piano colors are literals in draw_piano() and highlight() (canvas #2b2b2b, keys white/#111, active #dbe8ff/#7aa2ff, outline/label #333/#000/#555). The tk.Canvas, tk.Text log and root bg ignore ttk styles. No persisted settings exist. No UI tests exist (test_midi.py covers MIDI only).

1. TASK-003.01 Tokens: new theme.py with LIGHT and DARK palette dicts (bg, surface, fg, muted, border, accent, select_bg, piano_bg, key_white, key_black, key_white_active, key_black_active, key_outline, key_label, log_bg, log_fg). draw_piano() and highlight() read from the active palette instead of literals.
2. TASK-003.02 Apply: PianoApp.apply_theme(palette). Switch ttk to the cross-platform "clam" theme and configure TFrame, TLabel, TLabelframe, TButton, TCombobox, Horizontal.TScale, TScrollbar and the status label styles. Recolor root, canvas and log Text, option_add for the combobox dropdown list, then redraw the piano. Works on existing widgets, no restart.
3. TASK-003.03 OS detection: detect_system_theme() in theme.py. Windows: registry AppsUseLightTheme. macOS: defaults read -g AppleInterfaceStyle. Linux: gsettings org.gnome.desktop.interface color-scheme. Any failure returns light (documented fallback) and never raises.
4. TASK-003.04 Selector and persistence: "Megjelenes" combobox (Rendszer / Vilagos / Sotet) in the connection frame. Save choice as JSON in user config dir (%APPDATA%/synth-mido/settings.json, else ~/.config/synth-mido/settings.json). Missing or corrupt file falls back to System (default). Change applies immediately.
5. TASK-003.05 Live OS changes: while System is selected, poll detect_system_theme() every 2s via root.after and re-apply only on change. No threads. Explicit Light/Dark cancels the poll; on_close() cancels it too.
6. TASK-003.06 Polish: one font family/scale, consistent padding, accent color for active key, selection and Connect button, check contrast in both palettes, piano strip follows the palette.

Tests: new test_theme.py (pytest) covering palette key parity, settings load/save incl. corrupt file, OS detection with mocked registry/subprocess and the fallback path. UI wiring verified manually in Light, Dark and System, including switching OS theme live. Existing test_midi.py must stay green.
<!-- SECTION:PLAN:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The app offers Light, Dark, and System appearance modes
- [ ] #2 System is the default when no saved preference exists
- [ ] #3 Changing the mode updates the whole window, including ttk widgets, the piano canvas, and the log
- [ ] #4 The chosen mode is restored on the next launch
- [ ] #5 Connect, play, and listen behavior is unchanged
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in theme.py (palettes, OS detection, settings) and ui.py (apply_theme, selector, system-theme poll). Unit tests: test_theme.py, 16 tests green (python -m unittest test_theme). The Tk UI could not be launched in the Linux sandbox (no tkinter), so acceptance criteria are left unchecked until verified manually on Windows in Light, Dark and System mode, including switching the OS theme while the app runs.
<!-- SECTION:NOTES:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
