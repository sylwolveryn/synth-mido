# simple_test.py
import time

import mido

print("🎹 Zongora teszt - Microsoft GS Wavetable Synth")
print("=" * 40)

# Csatlakozás a Microsoft GS Wavetable Synth-hez
port_name = None
for name in mido.get_output_names():
    if "GENERAL" in name:
        port_name = name
        break

if not port_name:
    print("❌ GENERAL nem található!")
    exit()

print(f"✅ Csatlakozva: {port_name}")

try:
    with mido.open_output(port_name) as port:
        print("\n🎵 zongora teszt")
        # SysEx üzenetek - általános formátum
        # 0xF0 = SysEx kezdet, 0xF7 = SysEx vége

        print("\n🎵 Hangszer váltás: Akusztikus zongora")
        port.send(mido.Message('program_change', program=57))
        time.sleep(0.5)

        print("🎵 C-dúr skála játszása...")
        notes = [60, 62, 64, 65, 67, 69, 71, 72]
        for note in notes:
            port.send(mido.Message('program_change', program=note))
            port.send(mido.Message('note_on', note=note, velocity=100))
            print(f"  🔊 Hang: {note}")
            time.sleep(0.3)
            port.send(mido.Message('note_off', note=note, velocity=0))
            time.sleep(0.1)

        print("\n🎵 Hangszer váltás: Elektromos zongora")
        port.send(mido.Message('program_change', program=4))
        time.sleep(0.5)

        print("🎵 C-dúr akkord...")
        chord = [60, 64, 67]
        for note in chord:
            port.send(mido.Message('note_on', note=note, velocity=80))
        time.sleep(2.0)
        for note in chord:
            port.send(mido.Message('note_off', note=note, velocity=0))

        print("\n✅ Teszt kész!")

except Exception as e:
    print(f"❌ Hiba: {e}")
