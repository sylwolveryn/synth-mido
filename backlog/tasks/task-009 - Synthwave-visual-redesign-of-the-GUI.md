---
id: TASK-009
title: Synthwave visual redesign of the GUI
status: In Progress
assignee:
  - '@claude'
created_date: '2026-10-21T20:17:00Z'
updated_date: '2026-10-21T20:18:00Z'
labels:
  - feature
  - design
dependencies: []
references:
  - theme.py
  - ui.py
  - desktop-ui
  - theme
priority: medium
type: feature
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The app works, but it still looks like a plain Tk tool with a light/dark palette (TASK-003). The user wants a beautiful GUI in a Synthwave style: an 80s retro-futuristic look with a dark purple night sky, neon magenta and cyan accents, a sunset gradient and a perspective grid. It should feel like a synth instrument rather than a settings dialog.

Design direction (the template to follow):
- Palette tokens: background night #0d0221 / panel #1a0b3a / surface #261447, neon magenta #ff2a6d, neon cyan #05d9e8, sunset orange #ff9e00, sunset yellow #fdd835, text #f5e9ff, muted #b8a6d9, border #4d2a85.
- Header banner (Canvas): app title in large spaced capitals, a striped sunset sun over a perspective neon grid. It is decorative, cheap to draw and rescales with the window.
- Sections: dark panels with thin neon borders and uppercase, letter-spaced section titles. Primary actions are neon magenta, secondary ones are outlined.
- Piano: night-blue keybed; white keys with a subtle lavender tint; black keys deep purple; active keys glow cyan (white keys) / magenta (black keys); the keyboard range bar is the sunset gradient.
- Typography: system fonts only (Bahnschrift on Windows, falling back to Segoe UI / DejaVu Sans), no downloaded font files.

Decision: Synthwave becomes a fourth "Megjelenés" option and the default when no choice has been saved, replacing TASK-003's "Rendszer" default. A saved choice of Rendszer / Világos / Sötét is still respected, and all four themes keep working. Tk limitations apply: no real blur/glow, so glow is imitated with layered outlines and colour.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A "Synthwave" option appears in Megjelenés next to Rendszer / Világos / Sötét, is saved like the others, and is the default when no choice has been saved
- [ ] #2 The Synthwave palette uses the agreed tokens and every widget (buttons, comboboxes, sliders, checkbuttons, log, records window, save dialog, piano) is themed with no default-grey Tk parts left
- [ ] #3 A header banner shows the app title with a sunset sun and perspective grid in Synthwave, rescales with the window width, and is a plain compact title bar in the other themes
- [ ] #4 Section titles, buttons and borders follow the Synthwave design (neon primary buttons, outlined secondary buttons, uppercase section titles)
- [ ] #5 Piano keys, active-key highlight and the keyboard range bar use the Synthwave colours and stay clearly readable
- [ ] #6 Switching between all four themes at runtime works with no restart and no leftover colours
- [ ] #7 Text contrast is readable: body text and button labels have at least 4.5:1 contrast against their backgrounds in the Synthwave palette
- [ ] #8 All existing features keep working at the default and minimum window size
- [ ] #9 Unit tests cover the new palette (same tokens as the other palettes, contrast checks) and the new default theme
- [ ] #10 readme and a progress page show the new design with screenshots
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. theme.py: SYNTHWAVE_MODE with the agreed palette, plus shared tokens in every palette: accent2, section_fg, header_bg, title_fg, sun_top/sun_mid/sun_bottom and grid. MODES puts Synthwave first and DEFAULT_MODE becomes synthwave (this supersedes TASK-003). Add display_font(families), which prefers Bahnschrift, and a WCAG contrast() helper.
2. ui.py: a header banner canvas at the top. In Synthwave: a striped sunset sun, horizon, perspective grid, letter-spaced title with a magenta shadow and subtitle. In the other themes: a compact title bar. Both redraw on resize and theme change. apply_theme in Synthwave uses Bahnschrift, uppercase section titles in neon cyan, flat neon borders, magenta primary buttons with dark text, outlined secondary buttons, cyan slider handles, and a sunset-gradient keyboard range bar. "Synthwave" is added to Megjelenés. The window grows a little (860x830, minimum 780x720) for the header.
3. test_theme.py: default/fallback tests move to the new default, plus Synthwave palette key parity, contrast >= 4.5 for text/button pairs and the save/load round trip.
4. Smoke test switching all four themes at runtime, the records window and save dialog in Synthwave, default and minimum size, and screenshots. readme and progress page.
<!-- SECTION:PLAN:END -->
