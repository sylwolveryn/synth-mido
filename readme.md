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
