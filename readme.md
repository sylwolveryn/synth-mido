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

A program egy egyszerű ablakos felületet nyit: MIDI eszközök csatlakoztatása, hangszer választás, skála/akkord/bemutató, kattintható 88 billentyűs zongora (A0–C8, a C-k feliratozva, a középső C kiemelve) és billentyűzet-figyelés.

A haladás képernyőképekkel a [progress](progress/README.md) mappában követhető.

## Zongorázás a billentyűzettel

A zongora a számítógép billentyűzetéről is játszható (MIDI eszköz nélkül is), a zenei programokban megszokott két sorral:

```
   W   E       T   Z/Y  U       O   P
 A   S   D   F   G    H   J   K   L   É/;  Á/'
 C4  D4  E4  F4  G4   A4  B4  C5  D5  E5   F5
```

- Magyar QWERTZ és amerikai QWERTY kiosztáson is ugyanazokon a fizikai gombokon szól (a Z és Y is a G#).
- Több gomb együtt lenyomva akkordot ad; a lenyomva tartott gomb nem ismétel.
- A hangerő a "Hangerő" csúszkából jön; futó felvétel a billentyűzettel játszott hangokat is rögzíti.
- Szövegmezőben és Ctrl / Alt kombinációkkal nem szól; ha az ablak elveszti a fókuszt, minden lenyomott hang elhallgat.
- **X** egy oktávval lejjebb, **C** egy oktávval feljebb tolja a tartományt (vagy a zongora feletti ◀ / ▶ gombok); így az A0-tól a C8-ig minden billentyű elérhető. A kék sáv a zongora tetején mutatja az elérhető tartományt, a "Betűk a billentyűkön" kapcsolóval a gombok betűi is megjelennek.
- **Duplázás** ("két kéz", a "Lejátszás" sorban): Ki / +1 oktáv / −1 oktáv / ±1 oktáv — minden egérrel vagy billentyűzettel játszott hang egy oktávval lejjebb és/vagy feljebb is megszól, a felvétel is így rögzíti. A MIDI bemenet és a visszajátszás nem duplázódik. A választás mentődik.
- **Szóköz** = kitartó pedál: amíg lenyomva tartod, az elengedett billentyűk tovább szólnak (MIDI eszközre CC 64-ként megy ki, a tartalék kimeneten is működik). A "Pedál (Szóköz)" kapcsolóval egérrel is rögzíthető. A felvétel a ténylegesen szóló hosszt rögzíti.

## Hang MIDI eszköz nélkül

Ha nincs csatlakoztatott MIDI kimenet, a program a gép alapértelmezett hangkimenetét használja, így a képernyős zongora, a skála / akkord / bemutató gombok és a felvételek visszajátszása eszköz nélkül is hallható:

- **Windows:** a beépített *Microsoft GS Wavetable Synth* szól, a hangszerválasztás is működik.
- **Linux / macOS:** ha fut egy szoftveres szintetizátor (FluidSynth, TiMidity), annak a portját használja; különben egy egyszerű beépített hanggenerátor szól az alapértelmezett hangeszközön (`numpy` + `sounddevice`). Ez minden hangszert ugyanúgy szólaltat meg. Linuxon a `sounddevice`-hoz a PortAudio rendszercsomag kell (pl. `sudo apt install libportaudio2`).

Csatlakoztatott MIDI kimenet esetén mindig az szól; leválasztás után a program visszavált az alapértelmezett kimenetre. Az aktív hangkimenet az állapotsorban látható. Ha egyik kimenet sem érhető el, a program hang nélkül is működik (egyszer jelzi a naplóban).

Tesztek: `python -m unittest tests.test_audio_output -v`

## Téma

A felület négy megjelenést támogat, a "Megjelenés" legördülő listában választható, futás közben is:

- **Synthwave** (alapértelmezett) — 80-as évek retró-futurisztikus éjszakai stílusa: lila égbolt, neon magenta és cián, naplemente nap perspektivikus neon ráccsal a fejlécben, nagybetűs neon szakaszcímek, naplemente színátmenetű billentyűzet sáv. Betűtípus: Bahnschrift (ha nincs, Segoe UI / DejaVu Sans).
- **Rendszer** — az operációs rendszer világos/sötét beállítását követi, akár futás közben is.
- **Világos** és **Sötét**.

A választás a felhasználói konfigurációs mappába mentődik (`%APPDATA%\synth-mido\settings.json`, illetve `~/.config/synth-mido/settings.json`); a korábban mentett választás megmarad.

![Synthwave](progress/task-010-fx-synthwave.png)

### Hangvizualizáció

A zongora feletti sávban minden megszólaló hang neon oszlopot növeszt a billentyűje fölé (fehér billentyű: cián, fekete: magenta, a fényerő a hangerőtől függ); elengedéskor az oszlop tovább emelkedik és elhalványul, hangindításkor szikrák pattannak. Minden hangforrásra reagál: egér, billentyűzet, MIDI bemenet, felvétel lejátszás és a bemutató gombok. Az **Effekt** kapcsolóval ki- és bekapcsolható, a választás mentődik.

Tesztek: `python -m unittest tests.test_theme -v`

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

`start` és `duration` másodpercben értendő. Tesztek: `python -m unittest tests.test_recorder -v`

## Visszajátszás

Egy mentett felvétel kétféleképpen játszható le:

- a "Lejátszás" részben a **Felvétel lejátszása…** gombbal: fájlválasztó nyílik a `records/` mappában;
- a **Felvételek…** ablakban: jelölj ki egy felvételt és nyomd meg a **Lejátszás** gombot (vagy kattints duplán / Enter).

Betöltéskor a felvétel hangszere lesz kiválasztva a "Hangszer" listában, de lejátszás előtt vagy közben bármikor átállítható. A hangok az eredeti időzítéssel és hangerővel szólnak, a lejátszott billentyűk kiemelve látszanak a képernyős zongorán. MIDI eszköz nélkül az alapértelmezett hangkimeneten szól (lásd fent). A **Leállítás** és a **Minden hang ki** gomb azonnal megállítja; új lejátszás (felvétel, skála, akkord, bemutató) indítása leállítja az előzőt. A visszajátszás nem kerül bele egy éppen futó felvételbe.

### Lejátszó vezérlők

A betöltött felvétel a "Lejátszás" rész alsó sorában vezérelhető:

- **▶ / ⏸** — lejátszás és szünet; szünetben a hangok elhallgatnak, folytatáskor ugyanonnan szól tovább (a közben szóló hangok újraindulnak). A végére érve az elejéről indul újra.
- **■** — leállítás és visszatekerés az elejére (a felvétel betöltve marad). A **Leállítás** és a **Minden hang ki** gomb ugyanígy működik.
- **Pozíció csúszka** — mutatja, hol tart a lejátszás (`perc:mp / hossz`); rákattintva vagy húzva oda ugrik, lejátszás közben és szünetben is.
- **Sebesség** — 0.5x … 2x, lejátszás közben is azonnal vált, ugrás nélkül.

Tesztek: `python -m unittest tests.test_playback -v`

## Projekt felépítés

```
main.py                 belépési pont
synth_mido/
  config.py             MIDI csatorna, eszköz kulcsszavak, hangszerek
  core/                 Tk-tól független modellek (unit tesztelhetők)
    events.py           NoteBus — Observer: minden hang forrással együtt
    recorder.py         felvétel + JSON tárolás
    playback.py         lejátszó (szünet, ugrás, sebesség)
    piano_layout.py     88 billentyű geometria
    keyboard_play.py    számítógép billentyűzet, oktávváltás, pedál gomb
    sustain.py          kitartó pedál
    doubling.py         oktáv duplázás
  audio/                MIDI kimenet / bemenet és tartalék hanggenerátor
  skins/                témák / skinek (paletták, fejléc rajzolók)
  fx/                   vizuális effektek modelljei
  ui/                   Tk felület: app.py összerakja a részeket (mixinek)
tests/                  unit tesztek (+ fakes.py: közös hamis időzítő / port)
scripts/                hardver / diagnosztikai szkriptek (valódi eszközt igényelnek)
records/                felvételek (JSON)
progress/               haladás képernyőképekkel
```

Tervezési minták: **Observer** (`core/events.py` NoteBus — a zongora kiemelés, a hangvizualizáció és a hangszínszabályzó ablak feliratkozik a hangokra), **Facade** (`audio/midi_controller.py` — egy kimenet a csatlakoztatott eszköz vagy a tartalék előtt), **Strategy + Registry** (skinek fejléc rajzolói és az effekt animációk), Tk-tól független modellek + vékony nézet réteg.

Diagnosztika: `python -m scripts.examples`, `python scripts/diag.py`, `python scripts/midi_check.py`.

## Fejlesztés: pre-commit

Minden `git commit` előtt lefut a minőségkapu (`.pre-commit-config.yaml`): alap fájlellenőrzések, `ruff` lint és a `tests/` mappa összes unit tesztje (`python -m unittest discover -s tests -t .`). Egyszeri beállítás:

>pip install -r requirements-dev.txt
>pre-commit install

Kézi futtatás az összes fájlon: `pre-commit run --all-files`
