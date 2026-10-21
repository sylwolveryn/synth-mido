# usb_test.py
import mido
import time

print("USB MIDI teszt")
print("=" * 40)

# Az összes elérhető eszköz listázása
print("\n1. MIDI kimenetek:")
for i, name in enumerate(mido.get_output_names()):
    print(f"   {i}: {name}")

print("\n2. MIDI bemenetek:")
for i, name in enumerate(mido.get_input_names()):
    print(f"   {i}: {name}")

# Várjunk 5 másodpercet, hátha frissül a lista
print("\n⏳ Várakozás 5 másodpercet...")
time.sleep(5)

print("\n3. Újra ellenőrzés:")
print("   Bemenetek:", mido.get_input_names())
print("   Kimenetek:", mido.get_output_names())

# Ha van új eszköz, próbáljunk csatlakozni hozzá
all_devices = mido.get_output_names() + mido.get_input_names()
for device in all_devices:
    if "GENERAL" in device.upper() or "MIDI" in device.upper():
        print(f"\n✅ Megtalálva: {device}")
        try:
            with mido.open_output(device) as port:
                print("   Csatlakozva, teszt hang küldése...")
                port.send(mido.Message('note_on', note=60, velocity=100))
                time.sleep(0.5)
                port.send(mido.Message('note_off', note=60, velocity=0))
                print("   ✅ Hang elküldve!")
        except Exception as e:
            print(f"   ❌ Hiba: {e}")
