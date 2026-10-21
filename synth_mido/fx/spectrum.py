"""Hangszínszabályzó / spektrum modell (Tk-tól független).

Nincs hangfolyam, amiből FFT-t lehetne számolni, ezért a spektrumot a megszólaló
hangok adják: minden hang a hangmagasságának megfelelő frekvenciasávot táplálja
(a szomszéd sávokat és az oktávval feljebbit gyengébben, mint egy felhang), a
sávok gyorsan felfutnak és lassan lecsengenek, a csúcsjelzők kitartanak, majd
lehullanak — mint a régi Winamp analizátorban.
"""

import math
import time
from typing import Callable, Dict, List

from synth_mido.core.piano_layout import FIRST_NOTE, LAST_NOTE

BANDS = 24
ATTACK = 18.0        # 1/mp — milyen gyorsan éri el a sáv a célszintet
DECAY = 1.4          # szint / mp — lecsengés, ha a cél alacsonyabb
SUSTAIN = 0.85       # szóló hang ennyire tartja a sávját (a kezdeti ütés után)
PEAK_HOLD = 0.45     # mp — a csúcsjelző ennyi ideig marad
PEAK_FALL = 0.9      # szint / mp — utána ennyivel esik
NEIGHBOUR = 0.45     # szomszéd sáv hozzájárulása
OCTAVE = 0.35        # az egy oktávval feljebbi sáv (felhang) hozzájárulása


def band_of(note: int, bands: int = BANDS) -> int:
    """A hang sávja: A0 → 0, C8 → bands-1 (egyenletesen a 88 billentyűn)."""
    note = min(max(note, FIRST_NOTE), LAST_NOTE)
    return min(bands - 1, (note - FIRST_NOTE) * bands // (LAST_NOTE - FIRST_NOTE + 1))


class Spectrum:
    def __init__(self, bands: int = BANDS, clock: Callable[[], float] = time.monotonic):
        self.bands = bands
        self._clock = clock
        self.levels: List[float] = [0.0] * bands
        self.peaks: List[float] = [0.0] * bands
        self._peak_time: List[float] = [0.0] * bands
        self._sounding: Dict[int, float] = {}   # hang -> erő (0..1)
        self._kick: List[float] = [0.0] * bands  # hangindítás "ütése" (gyorsan lecseng)
        self._last = clock()
        self.time = 0.0

    # --- bemenet -----------------------------------------------------------------

    def note_on(self, note: int, velocity: int = 100) -> None:
        strength = max(1, min(velocity, 127)) / 127
        self._sounding[note] = strength
        for band, weight in self._contributions(note):
            self._kick[band] = max(self._kick[band], strength * weight)

    def note_off(self, note: int) -> None:
        self._sounding.pop(note, None)

    def clear(self) -> None:
        self._sounding.clear()
        self.levels = [0.0] * self.bands
        self.peaks = [0.0] * self.bands
        self._kick = [0.0] * self.bands

    def _contributions(self, note: int):
        b = band_of(note, self.bands)
        out = [(b, 1.0)]
        for nb in (b - 1, b + 1):
            if 0 <= nb < self.bands:
                out.append((nb, NEIGHBOUR))
        if note + 12 <= LAST_NOTE:
            out.append((band_of(note + 12, self.bands), OCTAVE))
        return out

    # --- időléptetés ---------------------------------------------------------------

    def step(self, now: float = None) -> None:
        now = self._clock() if now is None else now
        dt = min(max(now - self._last, 0.0), 0.25)
        self._last = now
        self.time = now
        target = [0.0] * self.bands
        for note, strength in self._sounding.items():
            for band, weight in self._contributions(note):
                # összeadódik: egy akkord jobban kitölti a sávjait, mint egy hang (felfelé 1-re vágva)
                target[band] = min(1.0, target[band] + strength * weight * SUSTAIN)
        for i in range(self.bands):
            self._kick[i] = max(0.0, self._kick[i] - DECAY * 1.5 * dt)
            goal = max(target[i], self._kick[i])
            level = self.levels[i]
            if goal > level:
                level += (goal - level) * min(1.0, ATTACK * dt)
            else:
                level = max(goal, level - DECAY * dt)
            self.levels[i] = level
            if level >= self.peaks[i]:
                self.peaks[i] = level
                self._peak_time[i] = now
            elif now - self._peak_time[i] > PEAK_HOLD:
                self.peaks[i] = max(level, self.peaks[i] - PEAK_FALL * dt)

    @property
    def active(self) -> bool:
        return bool(self._sounding) or any(v > 0.002 for v in self.levels) or any(v > 0.002 for v in self.peaks)

    def wave(self, samples: int, cycles: float = 3.0) -> List[float]:
        """Oszcilloszkóp minta (-1..1): a szóló hangok szinuszainak összege, a hangmagassággal arányos sűrűséggel."""
        if not self._sounding:
            return [0.0] * samples
        total = sum(self._sounding.values()) or 1.0
        out = []
        for i in range(samples):
            x = i / max(samples - 1, 1)
            v = 0.0
            for note, strength in self._sounding.items():
                freq = cycles * 2 ** ((note - 60) / 24)  # vizuálisan tömörített hangmagasság
                v += strength * math.sin(2 * math.pi * (freq * x + self.time * 0.8 * freq))
            out.append(max(-1.0, min(1.0, v / total)))
        return out
