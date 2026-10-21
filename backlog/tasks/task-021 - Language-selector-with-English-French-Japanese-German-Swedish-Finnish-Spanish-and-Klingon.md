---
id: TASK-021
title: >-
  Language selector with English, French, Japanese, German, Swedish, Finnish,
  Spanish and Klingon
status: Done
assignee:
  - '@claude'
created_date: '2026-10-21T22:47:00Z'
updated_date: '2026-10-21T23:18:00Z'
labels:
  - i18n
  - ui
dependencies: []
modified_files:
  - groma/actors/player.md
  - groma/systems/synth-mido/containers/desktop-app/components/connection.md
  - groma/systems/synth-mido/containers/desktop-app/components/i18n.md
  - groma/systems/synth-mido/containers/desktop-app/components/instrument-art.md
  - >-
    groma/systems/synth-mido/containers/desktop-app/components/instrument-view.md
  - groma/systems/synth-mido/containers/desktop-app/components/language.md
  - >-
    groma/systems/synth-mido/containers/desktop-app/components/midi-controller.md
  - >-
    groma/systems/synth-mido/containers/desktop-app/components/note-effect-view.md
  - groma/systems/synth-mido/containers/desktop-app/components/note-effect.md
  - groma/systems/synth-mido/containers/desktop-app/components/playback-view.md
  - groma/systems/synth-mido/containers/desktop-app/components/playback.md
  - groma/systems/synth-mido/containers/desktop-app/components/recorder.md
  - groma/systems/synth-mido/containers/desktop-app/components/theming.md
  - groma/systems/synth-mido/containers/desktop-app/components/tone-synth.md
  - groma/systems/synth-mido/containers/desktop-app/container.md
  - progress/README.md
  - progress/task-021-languages.png
  - progress/task-021.md
  - readme.md
  - synth_mido/audio/midi_controller.py
  - synth_mido/core/doubling.py
  - synth_mido/core/i18n.py
  - synth_mido/core/recorder.py
  - synth_mido/fx/animations.py
  - synth_mido/lang/de.json
  - synth_mido/lang/en.json
  - synth_mido/lang/es.json
  - synth_mido/lang/fi.json
  - synth_mido/lang/fr.json
  - synth_mido/lang/hu.json
  - synth_mido/lang/ja.json
  - synth_mido/lang/sv.json
  - synth_mido/lang/tlh.json
  - synth_mido/skins/painters.py
  - synth_mido/skins/registry.py
  - synth_mido/ui/app.py
  - synth_mido/ui/connection.py
  - synth_mido/ui/equalizer_window.py
  - synth_mido/ui/input.py
  - synth_mido/ui/instrument_view.py
  - synth_mido/ui/language.py
  - synth_mido/ui/piano_view.py
  - synth_mido/ui/playback_view.py
  - synth_mido/ui/recording.py
  - synth_mido/ui/records_window.py
  - synth_mido/ui/theming.py
  - tests/test_doubling.py
  - tests/test_i18n.py
  - tests/test_instrument_art.py
priority: high
type: feature
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every label is hard-coded in Hungarian. Players who do not read Hungarian need the UI in their language. Labels move into a language folder as simple key-value files (one per language) so they could later move into a database; switching the language reloads every label at once, which is cheap because the app is small.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All user-visible UI texts come from key-value language files in a language folder, Hungarian being the default and reference
- [x] #2 A language selector offers Magyar, English, Français, 日本語, Deutsch, Svenska, Suomi, Español and Klingon (tlhIngan Hol)
- [x] #3 Changing the language relabels the main window and open windows immediately and the choice is saved
- [x] #4 A missing key falls back to Hungarian, then to the key itself
- [x] #5 A test checks that every language file has exactly the keys of the reference file and valid placeholders
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. core/i18n.py: flat key-value JSON per language in synth_mido/lang/ (hu reference + en, fr, ja, de, sv, fi, es, tlh), t(key, **values) with hu -> key fallback, set_language reloads, language_name, upper() that keeps case-sensitive Klingon.
2. Move every user-visible text out of the UI and core (labels, buttons, titles, lists, status, logs, dialogs, record validation errors, skin/variant/doubling/animation names, header subtitle, illustration captions) into hu.json keys.
3. ui/language.py mixin: tr()/bind_text() register widget texts; set_language re-applies all live bindings (main window, Records, Equalizer), rebuilds language-dependent lists, status, player bar, sections; choice saved in settings. Language combobox next to Megjelenés; list choices by index.
4. Write the 8 translations; tests for key/placeholder parity, used keys, fallbacks; real-window smoke for live relabel, persistence and fit at 780 px in all languages; update Groma map, readme and progress.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Instrument names stay as General MIDI English names in every language. Language-dependent combobox choices are resolved by index. Klingon is never uppercased (case is phonemic). Japanese piano-row labels shortened to fit 780 px. Also removed a Windows username that had leaked into the Groma container overview in TASK-016 (cmd.exe expanded %APPDATA%), and curated the four new Groma components (i18n, language, instrument-art, instrument-view) with groups and relations.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added a language selector (Magyar, English, Français, 日本語, Deutsch, Svenska, Suomi, Español, tlhIngan Hol). All user-visible texts moved into flat key-value JSON files in synth_mido/lang/ with Hungarian as reference; core/i18n.py provides t() with Hungarian-then-key fallback and placeholder filling. Widgets bind their texts to keys, so a switch relabels the main window and the open Records and Equalizer windows at once, including lists, status, player bar, captions, dialogs and record validation errors; the choice is saved. Verified by 13 new unit tests (key and placeholder parity for all files, used keys exist, fallbacks) and a real-window smoke test (18/18) including fit at 780 px for all nine languages; earlier smoke tests still pass.
<!-- SECTION:FINAL_SUMMARY:END -->
