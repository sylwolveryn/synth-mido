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

## Hang MIDI eszköz nélkül

Ha nincs csatlakoztatott MIDI kimenet, a program a gép alapértelmezett hangkimenetét használja, így a képernyős zongora, a skála / akkord / bemutató gombok és a felvételek visszajátszása eszköz nélkül is hallható:

- **Windows:** a beépített *Microsoft GS Wavetable Synth* szól, a hangszerválasztás is működik.
- **Linux / macOS:** ha fut egy szoftveres szintetizátor (FluidSynth, TiMidity), annak a portját használja; különben egy egyszerű beépített hanggenerátor szól az alapértelmezett hangeszközön (`numpy` + `sounddevice`). Ez minden hangszert ugyanúgy szólaltat meg. Linuxon a `sounddevice`-hoz a PortAudio rendszercsomag kell (pl. `sudo apt install libportaudio2`).

Csatlakoztatott MIDI kimenet esetén mindig az szól; leválasztás után a program visszavált az alapértelmezett kimenetre. Az aktív hangkimenet az állapotsorban látható. Ha egyik kimenet sem érhető el, a program hang nélkül is működik (egyszer jelzi a naplóban).

Tesztek: `python -m unittest test_audio_output -v`

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

## Visszajátszás

Egy mentett felvétel kétféleképpen játszható le:

- a "Lejátszás" részben a **Felvétel lejátszása…** gombbal: fájlválasztó nyílik a `records/` mappában;
- a **Felvételek…** ablakban: jelölj ki egy felvételt és nyomd meg a **Lejátszás** gombot (vagy kattints duplán / Enter).

Betöltéskor a felvétel hangszere lesz kiválasztva a "Hangszer" listában, de lejátszás előtt vagy közben bármikor átállítható. A hangok az eredeti időzítéssel és hangerővel szólnak, a lejátszott billentyűk kiemelve látszanak a képernyős zongorán. MIDI eszköz nélkül az alapértelmezett hangkimeneten szól (lásd fent). A **Leállítás** és a **Minden hang ki** gomb azonnal megállítja; új lejátszás (felvétel, skála, akkord, bemutató) indítása leállítja az előzőt. A visszajátszás nem kerül bele egy éppen futó felvételbe.

Tesztek: `python -m unittest test_playback -v`

## Fejlesztés: pre-commit

Minden `git commit` előtt lefut a minőségkapu (`.pre-commit-config.yaml`): alap fájlellenőrzések, `ruff` lint és a `test_theme`, `test_recorder`, `test_audio_output`, `test_playback` unit tesztek. Egyszeri beállítás:

>pip install -r requirements-dev.txt
>pre-commit install

Kézi futtatás az összes fájlon: `pre-commit run --all-files`
