---
id: TASK-021
title: >-
  Language selector with English, French, Japanese, German, Swedish, Finnish,
  Spanish and Klingon
status: To Do
assignee: []
created_date: '2026-10-21T22:47:00Z'
labels:
  - i18n
  - ui
dependencies: []
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
- [ ] #1 All user-visible UI texts come from key-value language files in a language folder, Hungarian being the default and reference
- [ ] #2 A language selector offers Magyar, English, Français, 日本語, Deutsch, Svenska, Suomi, Español and Klingon (tlhIngan Hol)
- [ ] #3 Changing the language relabels the main window and open windows immediately and the choice is saved
- [ ] #4 A missing key falls back to Hungarian, then to the key itself
- [ ] #5 A test checks that every language file has exactly the keys of the reference file and valid placeholders
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->
