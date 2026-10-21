import mido
import time
import sys
from typing import Optional, List, Tuple
import config

class VevorMIDIController:
    """VEVOR digitális zongora MIDI vezérlője"""

    def __init__(self, channel: int = config.MIDI_CHANNEL):
        self.channel = channel
        self.input_port: Optional[mido.ports.BaseInput] = None
        self.output_port: Optional[mido.ports.BaseOutput] = None
        self.device_name: Optional[str] = None
        self.connected = False

        # Backend ellenőrzése
        self._check_backend()

    def _check_backend(self):
        """Ellenőrzi az elérhető MIDI backendeket"""
        print(f"🖥️  Operációs rendszer: {sys.platform}")

        try:
            # Mido verzió ellenőrzés (hiba nélkül)
            try:
                from importlib.metadata import version
                print(f"📦 Mido verzió: {version('mido')}")
            except Exception:
                pass

            # Teszteljük a get_input_names-t
            inputs = mido.get_input_names()
            print(f"✅ MIDI backend elérhető, {len(inputs)} bemenet található")
        except Exception as e:
            print(f"⚠️ MIDI backend probléma: {e}")
            print("   Próbáld: pip install python-rtmidi")

    def list_devices(self) -> Tuple[List[str], List[str]]:
        """Kilistázza az összes elérhető MIDI bemeneti és kimeneti eszközt"""
        try:
            inputs = mido.get_input_names()
            outputs = mido.get_output_names()
        except Exception as e:
            print(f"❌ Hiba az eszközök listázásakor: {e}")
            return [], []

        print("\n📥 Elérhető MIDI bemenetek:")
        if not inputs:
            print("  (Nincs elérhető bemenet)")
        for i, name in enumerate(inputs):
            print(f"  {i}: {name}")

        print("\n📤 Elérhető MIDI kimenetek:")
        if not outputs:
            print("  (Nincs elérhető kimenet)")
        for i, name in enumerate(outputs):
            print(f"  {i}: {name}")

        return inputs, outputs

    def find_vevor_device(self) -> bool:
        """Megkeresi a VEVOR eszközt a bemeneti és kimeneti portok között"""
        try:
            inputs, outputs = self.list_devices()
        except Exception as e:
            print(f"❌ Nem sikerült listázni az eszközöket: {e}")
            return False

        # Összes eszköz név keresése
        all_devices = list(set(inputs + outputs))

        # Először keressük a VEVOR-t
        for name in all_devices:
            name_upper = name.upper()
            if any(keyword.upper() in name_upper for keyword in config.DEVICE_NAME_KEYWORDS):
                self.device_name = name
                print(f"✅ VEVOR eszköz megtalálva: {name}")
                return True

        # Ha nem találjuk, próbáljuk az első MIDI eszközt
        if outputs:
            print(f"⚠️ VEVOR nem található, az első kimeneti eszközt használom: {outputs[0]}")
            self.device_name = outputs[0]
            return True
        elif inputs:
            print(f"⚠️ VEVOR nem található, az első bemeneti eszközt használom: {inputs[0]}")
            self.device_name = inputs[0]
            return True

        print("❌ Nem található MIDI eszköz!")
        print("   Ellenőrizd, hogy:")
        print("   1. A zongora be van kapcsolva")
        print("   2. USB kábel vagy Bluetooth csatlakoztatva van")
        print("   3. A zongorán be van kapcsolva a MIDI mód")
        return False

    def connect(
        self,
        device_name: Optional[str] = None,
        input_name: Optional[str] = None,
        output_name: Optional[str] = None,
    ) -> bool:
        """Csatlakozik a VEVOR zongorához"""
        try:
            if self.input_port or self.output_port:
                self.close()

            if input_name or output_name:
                self.device_name = output_name or input_name
                if output_name:
                    try:
                        self.output_port = mido.open_output(output_name)
                        print(f"✅ Kimenet megnyitva: {output_name}")
                    except Exception as e:
                        print(f"⚠️ Kimenet hiba: {e}")
                if input_name:
                    try:
                        self.input_port = mido.open_input(input_name)
                        print(f"✅ Bemenet megnyitva: {input_name}")
                    except Exception as e:
                        print(f"⚠️ Bemenet hiba: {e}")
                if not self.input_port and not self.output_port:
                    print("❌ Nem sikerült megnyitni a portokat!")
                    return False
                self.connected = True
                print(f"🔗 Csatlakozva: {self.device_name}")
                return True

            if device_name:
                self.device_name = device_name
            else:
                if not self.find_vevor_device():
                    return False

            # Próbáljuk megnyitni a kimenetet
            try:
                self.output_port = mido.open_output(self.device_name)
                print(f"✅ Kimenet megnyitva: {self.device_name}")
            except Exception as e:
                print(f"⚠️ Kimenet hiba: {e}")
                # Próbáljuk a nevet módosítani
                if "IN" in self.device_name:
                    alt_name = self.device_name.replace("IN", "OUT")
                    try:
                        self.output_port = mido.open_output(alt_name)
                        print(f"✅ Kimenet megnyitva: {alt_name}")
                    except Exception:
                        pass

            # Próbáljuk megnyitni a bemenetet
            try:
                self.input_port = mido.open_input(self.device_name)
                print(f"✅ Bemenet megnyitva: {self.device_name}")
            except Exception as e:
                print(f"⚠️ Bemenet hiba: {e}")
                if "OUT" in self.device_name:
                    alt_name = self.device_name.replace("OUT", "IN")
                    try:
                        self.input_port = mido.open_input(alt_name)
                        print(f"✅ Bemenet megnyitva: {alt_name}")
                    except Exception:
                        pass

            # Ha egyik sem sikerült, próbáljuk az összes eszközt
            if not self.output_port:
                all_outputs = mido.get_output_names()
                if all_outputs:
                    try:
                        self.output_port = mido.open_output(all_outputs[1])
                        print(f"✅ Kimenet megnyitva (General): {all_outputs[1]}")
                    except Exception:
                        pass

            if not self.input_port:
                all_inputs = mido.get_input_names()
                if all_inputs:
                    try:
                        self.input_port = mido.open_input(all_inputs[0])
                        print(f"✅ Bemenet megnyitva (első): {all_inputs[0]}")
                    except Exception:
                        pass

            # Ellenőrizzük, hogy sikerült-e
            if not self.input_port or not self.output_port:
                print("❌ Nem sikerült megnyitni a portokat!")
                print(f"   Bemenet: {self.input_port is not None}")
                print(f"   Kimenet: {self.output_port is not None}")
                return False

            self.connected = True
            print(f"🔗 Csatlakozva: {self.device_name}")
            return True

        except Exception as e:
            print(f"❌ Csatlakozási hiba: {e}")
            return False

    def note_on(self, note: int, velocity: int = 100) -> None:
        """Hang indítása (nem vár)"""
        if not self.connected or not self.output_port:
            print("❌ Nincs csatlakozás vagy kimenet!")
            return
        try:
            msg = mido.Message('note_on', channel=self.channel, note=note, velocity=velocity)
            self.output_port.send(msg)
        except Exception as e:
            print(f"❌ Hiba a hang küldésekor: {e}")

    def note_off(self, note: int) -> None:
        """Hang leállítása"""
        if not self.connected or not self.output_port:
            return
        try:
            msg = mido.Message('note_off', channel=self.channel, note=note, velocity=0)
            self.output_port.send(msg)
        except Exception as e:
            print(f"❌ Hiba a hang leállításakor: {e}")

    def send_note(self, note: int, velocity: int = 100, duration: float = 0.5) -> None:
        """Egy hang lejátszása a zongorán"""
        if not self.connected or not self.output_port:
            print("❌ Nincs csatlakozás vagy kimenet!")
            return

        try:
            self.note_on(note, velocity)
            print(f"🔊 Hang indítva: {note} (hangerő: {velocity})")

            time.sleep(duration)

            self.note_off(note)
            print(f"🔇 Hang leállítva: {note}")
        except Exception as e:
            print(f"❌ Hiba a hang küldésekor: {e}")

    def change_instrument(self, instrument_number: int) -> None:
        """Hangszer váltása Program Change üzenettel"""
        if not self.connected or not self.output_port:
            print("❌ Nincs csatlakozás vagy kimenet!")
            return

        try:
            pc = mido.Message('program_change', channel=self.channel, program=instrument_number)
            self.output_port.send(pc)

            instrument_name = self._find_instrument_name(instrument_number)
            print(f"🎹 Hangszer váltva: {instrument_name} (Program: {instrument_number})")
        except Exception as e:
            print(f"❌ Hiba a hangszer váltásakor: {e}")

    def _find_instrument_name(self, program_number: int) -> str:
        """Visszaadja a hangszín nevét a program szám alapján"""
        for name, num in config.INSTRUMENTS.items():
            if num == program_number:
                return name.replace('_', ' ').title()
        return f"Unknown ({program_number})"

    def play_chord(self, notes: List[int], velocity: int = 80, duration: float = 1.0) -> None:
        """Egy akkord lejátszása"""
        if not self.connected or not self.output_port:
            print("❌ Nincs csatlakozás vagy kimenet!")
            return

        try:
            print(f"🎵 Akkord indítva: {notes}")
            for note in notes:
                note_on = mido.Message('note_on', channel=self.channel, note=note, velocity=velocity)
                self.output_port.send(note_on)

            time.sleep(duration)

            for note in notes:
                note_off = mido.Message('note_off', channel=self.channel, note=note, velocity=0)
                self.output_port.send(note_off)
            print("🔇 Akkord leállítva")
        except Exception as e:
            print(f"❌ Hiba az akkord játszásakor: {e}")

    def read_messages(self) -> List[mido.Message]:
        """Beolvassa a beérkező MIDI üzeneteket"""
        if not self.connected or not self.input_port:
            return []

        messages = []
        try:
            for msg in self.input_port.iter_pending():
                messages.append(msg)
                print(f"📨 Üzenet: {msg}")
        except Exception as e:
            print(f"❌ Hiba az üzenetek olvasásakor: {e}")

        return messages

    def panic(self) -> None:
        """Összes hang leállítása"""
        if not self.connected or not self.output_port:
            return

        try:
            for note in range(128):
                note_off = mido.Message('note_off', channel=self.channel, note=note, velocity=0)
                self.output_port.send(note_off)
            print("🔇 Minden hang leállítva")
        except Exception as e:
            print(f"❌ Hiba a vészleállításkor: {e}")

    def close(self) -> None:
        """Kapcsolat bezárása"""
        try:
            if self.input_port:
                self.input_port.close()
                print("🔌 Bemenet bezárva")
            if self.output_port:
                self.output_port.close()
                print("🔌 Kimenet bezárva")
            self.input_port = None
            self.output_port = None
            self.connected = False
            print("🔌 Kapcsolat bontva")
        except Exception as e:
            print(f"⚠️ Hiba a kapcsolat bontásakor: {e}")
