#!/usr/bin/env python3
"""
VEVOR Digitális Zongora MIDI vezérlő
Mini MIDO projekt a VEVOR 88 billentyűs zongora vezérléséhez
"""

import sys
from midi_controller import VevorMIDIController
from examples import example_connect_and_play, example_listen_to_keyboard, example_demo

def show_menu():
    """Főmenü megjelenítése"""
    print("\n" + "=" * 50)
    print("🎹 VEVOR MIDI vezérlő")
    print("=" * 50)
    print("1. Csatlakozás és hangok lejátszása")
    print("2. Billentyűzet események figyelése")
    print("3. Bemutató (több hangszer)")
    print("4. MIDI eszközök listázása")
    print("0. Kilépés")
    print("=" * 50)

def list_devices():
    """Csak az eszközök listázása"""
    controller = VevorMIDIController()
    controller.list_devices()

def main():
    while True:
        show_menu()
        choice = input("\nVálassz egy opciót: ").strip()
        
        if choice == "1":
            example_connect_and_play()
        elif choice == "2":
            example_listen_to_keyboard()
        elif choice == "3":
            example_demo()
        elif choice == "4":
            list_devices()
        elif choice == "0":
            print("👋 Viszlát!")
            sys.exit(0)
        else:
            print("❌ Érvénytelen választás!")

if __name__ == "__main__":
    main()