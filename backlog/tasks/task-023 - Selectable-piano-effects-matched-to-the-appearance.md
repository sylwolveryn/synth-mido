---
id: TASK-023
title: Selectable piano effects matched to the appearance
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T23:58:00Z'
updated_date: '2026-10-22T00:11:00Z'
labels:
  - fx
  - ui
dependencies: []
priority: medium
type: feature
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The note effect above the keys is always the same flame. Each appearance should have its own matching effect (Volcano: fire, Sakura: cherry petals drifting away from the keys, Steampunk: steam puffs, ...), switched automatically with the appearance but still selectable by hand. Effects should be a plug-in style registry so new effects and skins are cheap to add.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 An effect selector sits next to the appearance selectors and lists every registered effect
- [x] #2 Changing the appearance switches to that skin's matching effect; the user can still pick another one
- [x] #3 Volcano uses the current fire, Sakura drifting petals, Steampunk steam, and every one of the 17 skins has a matching effect
- [x] #4 Effects are strategies in a registry with a shared interface, and a skin names its effect, so adding one needs no change to the view
- [x] #5 Every effect stays within the frame budget (capped shapes, pooled canvas items) and works with the Effekt on/off switch
- [x] #6 Tests cover the registry, the skin mapping and the behaviour of each effect
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Package synth_mido/fx/effects/: base NoteEffect (note_on/note_off/clear/active/frame) returning generic Shape(kind poly|oval|rect|line|text, role, points, intensity, black); LAYERS (role z-order), KINDS per role and colors(palette, dark) per effect; registry register/get/all/DEFAULT.
2. Effects: neon (restored original bars + sparks), flames (current), petals, steam/dust puffs, bubbles, snow, stars, leaves, pixels, glyphs (math / roman / notes / compass variants).
3. Skin gets an 'effect' field; catalog maps all 17 skins.
4. View: generic pooled renderer per role, rebuilt on effect switch; effect combobox next to the appearance selectors (language moves to its own row); skin change auto-switches; choice saved; i18n keys for effect names in all 9 languages.
5. Tests for registry, mapping, shared behaviour of every effect, specific petal/steam motion; smoke for switching, frame cost per effect, fit at 780x800; docs.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Language selector moved under the Refresh/Connect buttons so the effect selector fits the appearance row without extra height. A manual choice survives a dark/light change; a skin change switches to the skin effect. Glyph fonts are pre-loaded off-screen to avoid first-render stalls (up to 106 ms before). Groma: effect files combined into the note-effect component, stale visualizer.py detached.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced the single flame visualizer with a registry of 14 note effects (Strategy): neon, flames, petals, leaves, steam, dust, bubbles, snow, stars, pixels and four glyph sets. A shared NoteEffect base handles voices, particle emission, release and caps; effects only declare roles (layer, canvas kind, palette colour) and shapes, so the view renders any effect generically with pooled items. Every skin names its matching effect (Volcano flames, Sakura drifting petals, Steampunk steam, and so on); an effect selector next to the appearance switches automatically on skin change and can be overridden; names are translated in all 9 languages. Verified by 21 unit tests and a real-window smoke test (16/16) including frame cost per effect and a gallery.
<!-- SECTION:FINAL_SUMMARY:END -->
