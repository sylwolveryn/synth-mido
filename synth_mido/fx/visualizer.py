"""Synthwave hangvizualizáció — Tk-tól független modell.

Minden szóló hang neon oszlopot növeszt a billentyűje fölött; elengedéskor az
oszlop leválik, tovább emelkedik és elhalványul (csóva). Hangindításkor néhány
szikra pattan ki. A modell csak alakzatokat ad vissza (`frame`), a rajzolás a
felület dolga; az elemek száma korlátos, hogy sűrű játék se lassítson.
"""

import random
import time
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

RISE_SPEED = 140.0   # px / mp
TRAIL_LIFE = 1.6     # mp — elengedés után ennyi idő alatt halványul el
SPARK_LIFE = 0.4     # mp
SPARKS_PER_NOTE = 3
MAX_BARS = 96        # a vászon újrarajzolása a szűk keresztmetszet, ezért szigorú korlát
MAX_SPARKS = 60
MIN_INTENSITY = 0.02
GLOW_PAD = 3.0       # px — a "ragyogás" ennyivel szélesebb az oszlopnál


class Shape(NamedTuple):
    kind: str          # "glow" | "bar" | "spark"
    x0: float
    y0: float
    x1: float
    y1: float
    intensity: float   # 0..1 — a szín ennyire erős a háttérhez képest
    black: bool        # fekete billentyű (más szín)


class _Bar:
    __slots__ = ("note", "velocity", "start", "end")

    def __init__(self, note: int, velocity: int, start: float):
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end: Optional[float] = None


class _Spark:
    __slots__ = ("note", "start", "dx", "vx", "vy")

    def __init__(self, note: int, start: float, dx: float, vx: float, vy: float):
        self.note, self.start, self.dx, self.vx, self.vy = note, start, dx, vx, vy


def _base_intensity(velocity: int) -> float:
    return 0.45 + 0.55 * max(1, min(velocity, 127)) / 127


class Visualizer:
    def __init__(self, clock: Callable[[], float] = time.monotonic, seed: int = 7):
        self._clock = clock
        self._rng = random.Random(seed)
        self.bars: List[_Bar] = []
        self.sparks: List[_Spark] = []
        self._sounding: Dict[int, _Bar] = {}

    @property
    def active(self) -> bool:
        return bool(self.bars or self.sparks)

    def clear(self) -> None:
        self.bars.clear()
        self.sparks.clear()
        self._sounding.clear()

    def note_on(self, note: int, velocity: int = 100, t: Optional[float] = None) -> None:
        now = self._clock() if t is None else t
        if note in self._sounding:          # újraindítás: az előző oszlop leválik
            self._sounding[note].end = now
        bar = _Bar(note, velocity, now)
        self.bars.append(bar)
        self._sounding[note] = bar
        for _ in range(SPARKS_PER_NOTE):
            self.sparks.append(_Spark(
                note, now, self._rng.uniform(-0.3, 0.3), self._rng.uniform(-45, 45), self._rng.uniform(-170, -90)
            ))
        self._enforce_caps()

    def note_off(self, note: int, t: Optional[float] = None) -> None:
        bar = self._sounding.pop(note, None)
        if bar is not None:
            bar.end = self._clock() if t is None else t

    def _enforce_caps(self) -> None:
        if len(self.bars) > MAX_BARS:
            # a legrégebbi lecsengett oszlopok mennek először; szóló hang csak végső esetben
            ended = [b for b in self.bars if b.end is not None]
            drop = set(map(id, ended[: len(self.bars) - MAX_BARS]))
            self.bars = [b for b in self.bars if id(b) not in drop]
            while len(self.bars) > MAX_BARS:
                old = self.bars.pop(0)
                if self._sounding.get(old.note) is old:
                    del self._sounding[old.note]
        if len(self.sparks) > MAX_SPARKS:
            self.sparks = self.sparks[-MAX_SPARKS:]

    def frame(
        self, now: float, width: float, height: float, key_span: Callable[[int], Optional[Tuple[float, float, bool]]],
    ) -> List[Shape]:
        """A pillanatnyi alakzatok (hátulról előre), és közben a lejárt elemek törlése.

        `key_span(note)` → (x0, x1, fekete) a billentyű vízszintes helye, vagy None.
        """
        shapes: List[Shape] = []
        alive = []
        for bar in self.bars:
            span = key_span(bar.note)
            top = height - (now - bar.start) * RISE_SPEED
            if bar.end is None:
                bottom, fade = height, 1.0
            else:
                bottom = height - (now - bar.end) * RISE_SPEED
                fade = 1.0 - (now - bar.end) / TRAIL_LIFE
            intensity = _base_intensity(bar.velocity) * fade
            if bottom <= 0 or intensity < MIN_INTENSITY or span is None:
                continue
            alive.append(bar)
            x0, x1, black = span
            top = max(top, 0.0)
            if bar.end is None:
                shapes.append(Shape("glow", x0 - GLOW_PAD, top - GLOW_PAD, x1 + GLOW_PAD, bottom, intensity * 0.35, black))
            shapes.append(Shape("bar", x0, top, x1, bottom, intensity, black))
        self.bars = alive

        live_sparks = []
        for s in self.sparks:
            age = now - s.start
            span = key_span(s.note)
            if age > SPARK_LIFE or span is None:
                continue
            live_sparks.append(s)
            x0, x1, black = span
            cx = (x0 + x1) / 2 + s.dx * (x1 - x0) + s.vx * age
            cy = height + s.vy * age
            r = 1.5
            shapes.append(Shape("spark", cx - r, cy - r, cx + r, cy + r, 1.0 - age / SPARK_LIFE, black))
        self.sparks = live_sparks
        return shapes
