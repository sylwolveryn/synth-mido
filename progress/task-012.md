# TASK-012 — Refaktorálás csomagokba, tervezési mintákkal

**Állapot:** kész · 2026-10-21 · viselkedés változatlan (159 + 4 unit teszt, a korábbi ablak tesztek ugyanazt adják)

## Új felépítés

```mermaid
flowchart TB
    main["main.py"] --> app
    subgraph synth_mido
        config["config.py"]
        subgraph ui["ui/ — Tk nézet réteg"]
            app["app.py · PianoApp<br/>(összerakás + életciklus)"]
            mixins["theming · connection · playback_view · piano_view<br/>input · fx_view · recording · records_window"]
            common["common.py — állandók, segédek"]
            app --> mixins
        end
        subgraph core["core/ — Tk-tól független modellek"]
            events["events.py · NoteBus (Observer)"]
            rec["recorder"]
            pb["playback"]
            pl["piano_layout"]
            kp["keyboard_play"]
            su["sustain"]
            db["doubling"]
        end
        subgraph audio["audio/ — kimenet / bemenet"]
            mc["midi_controller (Facade)"]
            ts["tone_synth"]
        end
        skins["skins/ — téma / skinek"]
        fx["fx/ — effekt modellek"]
    end
    mixins --> core
    mixins --> audio
    mixins --> skins
    mixins --> fx
    mc --> ts
    tests["tests/ (+ fakes.py)"] -.-> core
    tests -.-> audio
    scripts["scripts/ — hardver szkriptek"] -.-> audio
```

## Observer: NoteBus

```mermaid
sequenceDiagram
    participant S as Hangforrás<br/>(egér · billentyűzet · MIDI be · lejátszás · bemutató)
    participant B as NoteBus
    participant K as Zongora kiemelés
    participant V as Hangvizualizáció
    participant E as Hangszínszabályzó ablak (TASK-014)
    S->>B: publish(note, on, velocity, source)
    B->>K: NoteEvent
    B->>V: NoteEvent
    B-->>E: NoteEvent (feliratkozik, ha nyitva)
```

## Mi változott

| Előtte | Utána |
|---|---|
| 17 modul a gyökérben, `ui.py` ~1400 sor | `synth_mido/` csomag: `core/`, `audio/`, `skins/`, `fx/`, `ui/`; a gyökérben csak `main.py` |
| `ui.py` mindent csinál | `ui/app.py` (~300 sor) + 8 fókuszált mixin modul + `common.py` |
| `highlight()` közvetlenül hívja a vizualizációt | `NoteBus.publish()` → feliratkozók (kiemelés, vizualizáció) — forrás címkével (`user`, `midi_in`, `playback`, `demo`) |
| tesztek a gyökérben, egymást importálják | `tests/` + `tests/fakes.py` (közös hamis időzítő / port / hanggenerátor) |
| `test_midi.py`, `diag.py`, `examples.py`, `usb.py` a gyökérben | `scripts/` (`test_midi.py` → `scripts/midi_check.py`, mert nem unit teszt) |
| pre-commit modul lista | `python -m unittest discover -s tests -t .` |

Fájlmozgatás `git mv`-vel, így az előzmények megmaradnak.
