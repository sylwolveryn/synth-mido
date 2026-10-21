## Install
### Windows
download and install
https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

Build Tools for Visual Studio 2026 -- direct link: https://aka.ms/vs/stable/vs_BuildTools.exe

>pip install -r requirements.txt

### Linux

pip install  -r requirements.txt

## Run

>py main.py

A program egy egyszerű ablakos felületet nyit: MIDI eszközök csatlakoztatása, hangszer választás, skála/akkord/bemutató, kattintható zongora és billentyűzet-figyelés.

## Téma

A felület Világos, Sötét és Rendszer megjelenést támogat (alapértelmezett: Rendszer, ami az operációs rendszer világos/sötét beállítását követi, akár futás közben is). A választás a "Megjelenés" legördülő listában állítható, és a felhasználói konfigurációs mappába mentődik (`%APPDATA%\synth-mido\settings.json`, illetve `~/.config/synth-mido/settings.json`).

Tesztek: `python -m unittest test_theme -v`

## Felvétel

A "Billentyűzet figyelése" részben a **● Felvétel** gombbal indítható a felvétel, a **■ Leállítás** gombbal áll le. Felvétel közben látszik az eltelt idő és a rögzített hangok száma.

- Rögzül a zongora (MIDI bemenet) és a képernyős zongora minden lenyomott hangja. Ha van bemenet, a felvétel automatikusan elindítja a figyelést.
- Kapcsolat nélkül is lehet felvenni ("vakon"): ilyenkor a képernyős zongora hangjai rögzülnek hang nélkül.
- A skála / akkord / bemutató gombok nem kerülnek a felvételbe.
- Leállításkor megadható a név (alapértelmezett: `felvetel_YYYYMMDD_HHMMSS`), vagy a felvétel elvethető. Leválasztáskor és kilépéskor a futó felvétel ugyanígy menthető.
- A **Felvételek…** ablak listázza az összes felvételt; egy vagy több kijelölt (Ctrl / Shift) felvétel egyszerre törölhető.

A felvételek a program mappájában, a `records/` alatt, JSON fájlként tárolódnak. Csak a hangokat, az időzítést és a használt hangszert tartalmazzák (a hangszer visszajátszáskor csak alapértelmezés):

```json
{
  "format": "synth-mido-record",
  "version": 1,
  "created": "2026-10-21T19:40:12",
  "instrument": {"name": "acoustic_grand_piano", "program": 0},
  "duration": 12.48,
  "notes": [{"note": 60, "velocity": 100, "start": 0.0, "duration": 0.42}]
}
```

`start` és `duration` másodpercben értendő. Tesztek: `python -m unittest test_recorder -v`

## Fejlesztés: pre-commit

Minden `git commit` előtt lefut a minőségkapu (`.pre-commit-config.yaml`): alap fájlellenőrzések, `ruff` lint és a `test_theme`, `test_recorder` unit tesztek. Egyszeri beállítás:

>pip install -r requirements-dev.txt
>pre-commit install

Kézi futtatás az összes fájlon: `pre-commit run --all-files`
