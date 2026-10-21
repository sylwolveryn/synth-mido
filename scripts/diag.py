# diagnose_midi.py
import sys

import mido

print("=" * 50)
print("MIDI Diagnosztika")
print("=" * 50)

print(f"\nPython verzió: {sys.version}")

# Mido verzió lekérése (új mód)
try:
    from importlib.metadata import version
    print(f"Mido verzió: {version('mido')}")
except Exception:
    try:
        print(f"Mido verzió: {mido.__version__}")
    except AttributeError:
        print("Mido verzió: (nem elérhető)")

print("\n--- MIDI Backendek ---")
try:
    # Mido 1.3.x backend ellenőrzés
    if hasattr(mido, 'backend'):
        print(f"Backend típusa: {type(mido.backend)}")
        if hasattr(mido.backend, '_backends'):
            print(f"Elérhető backendek: {list(mido.backend._backends.keys())}")
except Exception as e:
    print(f"  ℹ️  {e}")

print("\n--- MIDI Bemenetek ---")
try:
    inputs = mido.get_input_names()
    if inputs:
        for i, name in enumerate(inputs):
            print(f"  {i}: {name}")
    else:
        print("  (Nincs elérhető bemenet)")
except Exception as e:
    print(f"  ❌ Hiba: {e}")

print("\n--- MIDI Kimenetek ---")
try:
    outputs = mido.get_output_names()
    if outputs:
        for i, name in enumerate(outputs):
            print(f"  {i}: {name}")
    else:
        print("  (Nincs elérhető kimenet)")
except Exception as e:
    print(f"  ❌ Hiba: {e}")

# Próbáljunk csatlakozni az első kimenethez
if outputs:
    print("\n--- Teszt csatlakozás ---")
    try:
        with mido.open_output(outputs[0]) as port:
            print(f"✅ Csatlakozva: {outputs[0]}")

            # Teszt üzenet küldése
            msg = mido.Message('note_on', note=30, velocity=100)
            port.send(msg)
            print("✅ Note On üzenet elküldve (C4)")

            import time
            time.sleep(0.5)

            msg = mido.Message('note_off', note=60, velocity=0)
            port.send(msg)
            print("✅ Note Off üzenet elküldve")
    except Exception as e:
        print(f"❌ Hiba: {e}")
else:
    print("\n❌ Nincs MIDI kimenet!")
    print("   Ellenőrizd a csatlakozást!")
    print("\n💡 Tippek:")
    print("   1. A zongora legyen bekapcsolva")
    print("   2. USB kábel csatlakoztatva")
    print("   3. Bluetooth párosítva (ha azt használsz)")
    print("   4. A zongorán legyen bekapcsolva a MIDI mód")
