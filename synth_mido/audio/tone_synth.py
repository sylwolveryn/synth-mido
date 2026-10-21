"""Egyszerű hanggenerátor — tartalék hangkimenet, ha nincs MIDI szintetizátor.

A `ToneSynth` úgy viselkedik, mint egy mido kimeneti port (`send`, `close`, `name`):
a note_on / note_off üzenetekből lecsengő szinusz hangokat kever, és a gép
alapértelmezett hangeszközén (sounddevice) szólaltatja meg. A hangszínt nem
követi — minden hangszer ugyanúgy szól —, de a csatornákat külön kezeli, így két
hangszer azonos hangja egymástól függetlenül szól és áll le.

A numpy és a sounddevice csak példányosításkor töltődik be, így hiányuk nem
akadályozza a program indítását.
"""

import threading

SAMPLE_RATE = 44100
ATTACK = 0.005      # mp
RELEASE = 0.12      # mp
DECAY_RATE = 1.6    # 1/mp — lassú, zongoraszerű lecsengés
SILENCE = 0.001     # ennyi alatti burkolójú hangot eldobunk
GAIN = 0.25
HARMONICS = ((1, 1.0), (2, 0.35), (3, 0.12))
ALL_NOTES_OFF_CONTROLS = (120, 123)  # All Sound Off, All Notes Off


class ToneSynthUnavailable(RuntimeError):
    """A hanggenerátor nem indítható (hiányzó könyvtár vagy hangeszköz)."""


def note_frequency(note: int) -> float:
    return 440.0 * 2 ** ((note - 69) / 12)


class _Voice:
    __slots__ = ("freq", "amp", "pos", "release_pos")

    def __init__(self, freq: float, amp: float):
        self.freq = freq
        self.amp = amp
        self.pos = 0              # eddig lejátszott minták száma
        self.release_pos = None   # a felengedés mintaszáma


class ToneSynth:
    name = "Beépített hanggenerátor"

    def __init__(self, samplerate: int = SAMPLE_RATE, start_stream: bool = True):
        try:
            import numpy as np
        except ImportError as e:
            raise ToneSynthUnavailable("a numpy nincs telepítve") from e
        self._np = np
        self.samplerate = samplerate
        self._voices = {}
        self._lock = threading.Lock()
        self._stream = None
        if start_stream:
            try:
                import sounddevice as sd
            except (ImportError, OSError) as e:
                raise ToneSynthUnavailable(f"a sounddevice nem tölthető be ({e})") from e
            try:
                self._stream = sd.OutputStream(
                    samplerate=samplerate, channels=1, dtype="float32", callback=self._callback
                )
                self._stream.start()
            except Exception as e:
                raise ToneSynthUnavailable(f"nincs használható hangeszköz ({e})") from e

    # --- mido port felület -------------------------------------------------

    def send(self, msg) -> None:
        if msg.type == "note_on" and msg.velocity > 0:
            with self._lock:
                self._voices[(msg.channel, msg.note)] = _Voice(note_frequency(msg.note), msg.velocity / 127)
        elif msg.type in ("note_on", "note_off"):
            with self._lock:
                voice = self._voices.get((msg.channel, msg.note))
                if voice is not None and voice.release_pos is None:
                    voice.release_pos = voice.pos
        elif msg.type == "control_change" and msg.control in ALL_NOTES_OFF_CONTROLS:
            with self._lock:
                self._voices.clear()
        # program_change és minden más: nincs hatása

    def close(self) -> None:
        with self._lock:
            self._voices.clear()
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            finally:
                self._stream = None

    @property
    def active_notes(self):
        with self._lock:
            return sorted({note for _, note in self._voices})

    # --- hangkeverés -------------------------------------------------------

    def render(self, frames: int):
        """A következő `frames` minta (float32, -1..1) — eszköz nélkül is hívható."""
        np = self._np
        out = np.zeros(frames, dtype=np.float64)
        n = np.arange(frames)
        sr = self.samplerate
        with self._lock:
            for key, v in list(self._voices.items()):
                samples = v.pos + n
                t = samples / sr
                wave = sum(weight * np.sin(2 * np.pi * v.freq * k * t) for k, weight in HARMONICS)
                env = np.minimum(t / ATTACK, 1.0) * np.exp(-DECAY_RATE * t)
                if v.release_pos is not None:
                    since = (samples - v.release_pos) / sr
                    env = env * np.clip(1.0 - since / RELEASE, 0.0, 1.0)
                out += wave * env * v.amp
                v.pos += frames
                ended = v.release_pos is not None and (v.pos - v.release_pos) / sr >= RELEASE
                faded = np.exp(-DECAY_RATE * v.pos / sr) < SILENCE
                if ended or faded:
                    del self._voices[key]
        return np.tanh(out * GAIN).astype(np.float32)

    def _callback(self, outdata, frames, _time, _status):
        outdata[:, 0] = self.render(frames)
