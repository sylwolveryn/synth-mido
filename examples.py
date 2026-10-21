from midi_controller import VevorMIDIController
import config
import time

def example_connect_and_play():
    """Példa: Csatlakozás és néhány hang lejátszása"""
    print("🎹 VEVOR MIDI vezérlő - Alap példa")
    print("=" * 50)

    # Vezérlő létrehozása
    controller = VevorMIDIController()

    # Csatlakozás
    if not controller.connect():
        return

    try:
        # 1. Hangszer váltás zongorára (0)
        print("\n1. Hangszer váltás: Akusztikus zongora")
        controller.change_instrument(0)
        time.sleep(0.5)

        # 2. Egyszerű dallam (C-dúr skála)
        print("\n2. C-dúr skála játszása")
        c_major_scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C, D, E, F, G, A, B, C
        for note in c_major_scale:
            controller.send_note(note, velocity=100, duration=0.3)
            time.sleep(0.1)

        # 3. Akkord (C-dúr)
        print("\n3. C-dúr akkord")
        controller.play_chord([60, 64, 67], velocity=80, duration=2.0)

        # 4. Hangszer váltás (Elektromos zongora)
        print("\n4. Hangszer váltás: Elektromos zongora")
        controller.change_instrument(4)  # Electric Piano 1
        time.sleep(0.5)

        # 5. Még egy akkord
        print("\n5. G-dúr akkord (elektromos zongorán)")
        controller.play_chord([67, 71, 74], velocity=80, duration=2.0)

    finally:
        # Kapcsolat bontása
        controller.close()

def example_listen_to_keyboard():
    """Példa: Billentyűzet események figyelése"""
    print("🎹 VEVOR MIDI vezérlő - Billentyűzet figyelés")
    print("=" * 50)
    print("Játssz a zongorán, és figyeld a kimenetet!")
    print("Nyomj Ctrl+C-t a kilépéshez\n")

    controller = VevorMIDIController()

    if not controller.connect():
        return

    try:
        print("👂 Figyelés indítva...")
        print("   (Játssz valamit a zongorán, és itt megjelennek az események)")
        print("   Kilépés: Ctrl+C\n")

        while True:
            # Üzenetek fogadása a bemenetről
            for msg in controller.input_port.iter_pending():
                if msg.type in ['note_on', 'note_off']:
                    action = "ON " if msg.velocity > 0 else "OFF"
                    print(f"  {action} Note: {msg.note} (Hangerő: {msg.velocity})")
                elif msg.type == 'control_change':
                    print(f"  CC {msg.control} -> {msg.value}")
                elif msg.type == 'program_change':
                    print(f"  PC -> {msg.program}")
                else:
                    print(f"  {msg}")

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n\n⏹️ Figyelés leállítva")
    finally:
        controller.close()

def example_demo():
    """Bemutató: Hangszer váltás, dallam, akkordok"""
    print("🎹 VEVOR MIDI vezérlő - Bemutató")
    print("=" * 50)

    controller = VevorMIDIController()

    if not controller.connect():
        return

    try:
        # Különböző hangszerek bemutatása
        instruments = [
            # (0, "Akusztikus zongora"),
            (4, "Elektromos zongora 1")
            # (18, "Rock orgona"),
            # (24, "Akusztikus gitár"),
            # (40, "Hegedű"),
            # (48, "Vonósok"),
            # (56, "Trombita"),
            # (80, "Szintetizátor (Square)")
        ]

        for program_num, name in instruments:
            print(f"\n🎵 {name}")
            controller.change_instrument(program_num)
            time.sleep(0.5)

            # Egyszerű dallam
            melody = [76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 68, 71, 72, 64, 76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 72, 71, 69, 76, 75, 76, 75, 76, 71, 72, 74, 69, 60, 64, 69, 71, 64, 68, 71, 72, 64, 76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 72, 71, 69, 71, 72, 74, 76, 67, 77, 76, 74, 65, 76, 74, 72, 64, 74, 72, 71, 64, 76, 76, 90, 75, 76, 75, 76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 68, 71, 72, 64, 76, 75, 76, 75, 76, 71, 74, 72, 69]
            for note in melody:
                controller.send_note(note, velocity=90, duration=0.5)
                time.sleep(0.15)

            time.sleep(0.5)

        print("\n✨ Bemutató vége!")

    finally:
        controller.close()

if __name__ == "__main__":
    # A kívánt példa futtatása
    # example_connect_and_play()
    # example_listen_to_keyboard()
    example_demo()
