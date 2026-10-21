# TASK-018 — Hibakereső gombok eltávolítása

**Állapot:** kész · 2026-10-22

A **Lejátszás** sorából kikerültek a korai teszt gombok: **Skála**, **Akkord**, **Bemutató** és **Minden hang ki** (ez a **Leállítás** másolata volt). A sorban a **Megnyitás…** és a **Leállítás** maradt; a Leállítás megállítja a felvétel lejátszását, felengedi a pedált és minden szóló hangot elhallgattat.

| Előtte | Utána |
|---|---|
| Skála · Akkord · Bemutató · Megnyitás… · Leállítás · Minden hang ki | Megnyitás… · Leállítás |

Törölt kód: a skála / akkord / bemutató lejátszó (`play_scale`, `play_chord`, `play_demo`, `_play_sequence` …), a hozzájuk tartozó állapot (`playing`, `play_job`), a `C_MAJOR_SCALE`, `C_MAJOR_CHORD`, `DEMO_MELODY` állandók és a `DEMO` hangforrás.

## Ellenőrzés

- 196 unit teszt zöld, ruff tiszta.
- Valós ablak: 3/3 — csak a két gomb maradt, egy felvétel lejátszása közben a Leállítás megállítja a lejátszót, felengedi a pedált és nem marad kiemelt billentyű.
- A Lejátszás sor képe: [TASK-022](task-022.md).
