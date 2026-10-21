---
id: TASK-001
title: Precommit hook setup
status: Done
assignee: []
created_date: '2026-10-21T15:57:00Z'
updated_date: '2026-10-21T17:34:00Z'
labels: []
dependencies: []
ordinal: 8000
---

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Current state: the task only has a title. No pre-commit tooling exists (no .pre-commit-config.yaml, only sample hooks in .git/hooks, no core.hooksPath). Python files are mostly CRLF (config, midi_controller, main, ...); three .pyc files are tracked in git despite .gitignore. The only tests are test_theme.py (unittest; test_midi.py is a hardware script that runs at import, so it is not a gate). Neither ruff nor pre-commit was installable in the sandbox, so the config is untested here.

Approach: use the pre-commit framework so the same gate runs on Windows and Linux.
1. .pre-commit-config.yaml: pre-commit-hooks (check-yaml, check-merge-conflict, check-added-large-files, end-of-file-fixer, trailing-whitespace), ruff lint only (no auto-fix, no formatter, so existing code is never rewritten), and a local hook running `python -m unittest test_theme` (language: python, so it uses pre-commit's own env on any OS). backlog/ and groma/ are excluded because those files are tool-managed; .pyc files excluded.
2. ruff.toml: default rules; per-file ignore F401 for examples.py (existing unused import in a scratch script). No mixed-line-ending hook, since the repo is CRLF/LF mixed.
3. requirements-dev.txt with pre-commit.
4. readme.md: short setup section (pip install -r requirements-dev.txt, pre-commit install, pre-commit run --all-files).
5. Not done by me: `pre-commit install` must be run by the user on their own machine (the sandbox is Linux and would write a hook with the wrong interpreter path into the Windows repo's .git).
<!-- SECTION:PLAN:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 tests have been ran and they are green
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added .pre-commit-config.yaml, ruff.toml, requirements-dev.txt and a readme section. No application code changed. Config is syntactically valid YAML but could not be executed in the sandbox (pre-commit/ruff not installable there). To activate: pip install -r requirements-dev.txt, pre-commit install, then pre-commit run --all-files to verify. Hook revs (pre-commit-hooks v5.0.0, ruff-pre-commit v0.8.6) can be bumped with pre-commit autoupdate.
<!-- SECTION:NOTES:END -->
