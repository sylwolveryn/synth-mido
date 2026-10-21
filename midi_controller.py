import mido
import time
import sys
from typing import Callable, Optional, List, Tuple
import config
from tone_synth import ToneSynth

class VevorMIDIController:
    """VEVOR digitális zongora MIDI vezérlője"""

    def __init__(self, channel: int = config.MIDI_CHANNEL, tone_factory: Callable = ToneSynth):
        self.channel = channel
        self.input_port: Optional[mido.ports.BaseInput] = None
        self.output_port: Optional[mido.ports.BaseOutput] = None
        self.device_name: Optional[str] = None
        self.connected = False

        # Tartalék kimenet, ha nincs csatlakoztatott MIDI kimenet (lustán nyílik meg)
        self._tone_factory = tone_factory
        self.fallback = None
        self.fallback_name: Optional[str] = None
        self.fallback_error: Optional[str] = None

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
            # A tartalék port (pl. GS szintetizátor) lehet az új kimenet is — előbb elengedjük
            self._close_fallback()

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

    # --- hangkimenet: csatlakoztatott port vagy tartalék --------------------

    @property
    def active_output(self):
        """A hangok kimenete: a csatlakoztatott MIDI kimenet, különben a tartalék (szükség esetén megnyitja)."""
        if self.connected and self.output_port:
            return self.output_port
        return self._ensure_fallback()

    @property
    def output_name(self) -> Optional[str]:
        if self.connected and self.output_port:
            return self.output_port.name
        if self._ensure_fallback() is not None:
            return self.fallback_name
        return None

    @property
    def using_fallback(self) -> bool:
        return not (self.connected and self.output_port) and self._ensure_fallback() is not None

    def _ensure_fallback(self):
        if self.fallback is None and self.fallback_error is None:
            self.fallback = self._open_fallback()
        return self.fallback

    def _open_fallback(self):
        """Az OS szintetizátor portja, ha van; különben a beépített hanggenerátor."""
        try:
            names = mido.get_output_names()
        except Exception:
            names = []
        for name in names:
            if any(k in name.upper() for k in config.FALLBACK_SYNTH_KEYWORDS):
                try:
                    port = mido.open_output(name)
                    self.fallback_name = name
                    print(f"🔈 Alapértelmezett hangkimenet: {name}")
                    return port
                except Exception as e:
                    print(f"⚠️ {name} nem nyitható meg: {e}")
        try:
            synth = self._tone_factory()
            self.fallback_name = synth.name
            print(f"🔈 Alapértelmezett hangkimenet: {synth.name}")
            return synth
        except Exception as e:
            self.fallback_error = f"Nincs alapértelmezett hangkimenet: {e}"
            print(f"⚠️ {self.fallback_error}")
            return None

    def _close_fallback(self) -> None:
        if self.fallback is not None:
            try:
                self.fallback.close()
            except Exception as e:
                print(f"⚠️ Hiba a tartalék kimenet bezárásakor: {e}")
            self.fallback = None
            self.fallback_name = None

    def _send(self, msg: mido.Message, open_fallback: bool = True) -> bool:
        """Üzenet küldése az aktív kimenetre; False, ha nincs kimenet vagy hiba történt."""
        if self.connected and self.output_port:
            port = self.output_port
        else:
            port = self._ensure_fallback() if open_fallback else self.fallback
        if port is None:
            return False
        try:
            port.send(msg)
            return True
        except Exception as e:
            print(f"❌ Hiba az üzenet küldésekor: {e}")
            return False

    def note_on(self, note: int, velocity: int = 100) -> None:
        """Hang indítása (nem vár)"""
        self._send(mido.Message('note_on', channel=self.channel, note=note, velocity=velocity))

    def note_off(self, note: int) -> None:
        """Hang leállítása"""
        self._send(mido.Message('note_off', channel=self.channel, note=note, velocity=0), open_fallback=False)

    def send_note(self, note: int, velocity: int = 100, duration: float = 0.5) -> None:
        """Egy hang lejátszása a zongorán"""
        if self.active_output is None:
            print("❌ Nincs hangkimenet!")
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
        pc = mido.Message('program_change', channel=self.channel, program=instrument_number)
        if self._send(pc):
            instrument_name = self._find_instrument_name(instrument_number)
            print(f"🎹 Hangszer váltva: {instrument_name} (Program: {instrument_number})")

    def _find_instrument_name(self, program_number: int) -> str:
        """Visszaadja a hangszín nevét a program szám alapján"""
        for name, num in config.INSTRUMENTS.items():
            if num == program_number:
                return name.replace('_', ' ').title()
        return f"Unknown ({program_number})"

    def play_chord(self, notes: List[int], velocity: int = 80, duration: float = 1.0) -> None:
        """Egy akkord lejátszása"""
        if self.active_output is None:
            print("❌ Nincs hangkimenet!")
            return

        print(f"🎵 Akkord indítva: {notes}")
        for note in notes:
            self.note_on(note, velocity)

        time.sleep(duration)

        for note in notes:
            self.note_off(note)
        print("🔇 Akkord leállítva")

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
        """Összes hang leállítása (a már megnyitott tartalék kimeneten is)"""
        sent = self._send(
            mido.Message('control_change', channel=self.channel, control=123, value=0), open_fallback=False
        )
        if not sent:
            return
        for note in range(128):
            self._send(mido.Message('note_off', channel=self.channel, note=note, velocity=0), open_fallback=False)
        print("🔇 Minden hang leállítva")

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

    def shutdown(self) -> None:
        """Kilépéskor: a kapcsolat és a tartalék kimenet bezárása"""
        if self.input_port or self.output_port:
            self.close()
        self._close_fallback()
