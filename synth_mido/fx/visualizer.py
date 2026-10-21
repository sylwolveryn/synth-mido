"""Lángoló hangvizualizáció — Tk-tól független modell.

Minden szóló hang egy lobogó lángot gyújt a billentyűje fölött: puha fényudvar
(három réteg), színes külső láng és világos mag. A láng magassága a hangerőtől függ,
amíg a hang szól, lobog és parazsat szór; elengedéskor összehúzódik és kialszik.
A modell csak alakzatokat ad vissza (`frame`), a rajzolás és a színezés a felület
dolga; az elemek száma korlátos, hogy sűrű játék se lassítson.
"""

import math
import random
import time
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

ATTACK = 0.08          # mp — ennyi idő alatt csap fel teljes magasságra
FADE = 0.55            # mp — elengedés után ennyi idő alatt alszik ki
MIN_HEIGHT = 0.35      # a sáv magasságához képest, halk hangnál …
MAX_HEIGHT = 0.95      # … és teljes hangerőnél
WIDTH_FACTOR = 2.1     # a láng szélessége a billentyű szélességéhez képest
CORE_WIDTH = 0.45      # a mag a lánghoz képest
CORE_HEIGHT = 0.6
HALO_WIDTH = (3.0, 2.2, 1.5)  # a fényudvar rétegei (kívülről befelé) a láng szélességéhez képest
HALO_LEVEL = (0.08, 0.15, 0.26)  # lépcsőzetes, halvány rétegek: puha átmenet
EMBER_LIFE = 0.9       # mp
EMBER_RATE = 7.0       # parázs / mp lángonként, amíg a hang szól
EMBER_BURST = 4        # gyújtáskor kipattanó parázs
MAX_FLAMES = 40        # a vászon újrarajzolása a szűk keresztmetszet, ezért szigorú korlát
MAX_EMBERS = 70
MIN_INTENSITY = 0.03
SIDE_POINTS = (0.22, 0.48, 0.74)  # a láng oldalpontjai a magasság arányában


class Shape(NamedTuple):
    kind: str                   # "halo" | "flame" | "core" | "ember"
    points: Tuple[float, ...]   # sokszög (flame, core) vagy befoglaló téglalap (halo, ember)
    intensity: float            # 0..1 — a szín ennyire erős a háttérhez képest
    black: bool                 # fekete billentyű (más árnyalat)


class _Flame:
    __slots__ = ("note", "velocity", "start", "end", "phase", "carry")

    def __init__(self, note: int, velocity: int, start: float, phase: float):
        self.note = note
        self.velocity = velocity
        self.start = start
        self.end: Optional[float] = None
        self.phase = phase      # minden láng a saját ritmusában lobog
        self.carry = 0.0        # parázskibocsátás tört része képkockák között


class _Ember:
    __slots__ = ("note", "start", "dx", "vx", "vy", "size", "phase")

    def __init__(self, note, start, dx, vx, vy, size, phase):
        self.note, self.start, self.dx, self.vx, self.vy, self.size, self.phase = note, start, dx, vx, vy, size, phase


def _base_intensity(velocity: int) -> float:
    return 0.5 + 0.5 * max(1, min(velocity, 127)) / 127


def _height_ratio(velocity: int) -> float:
    return MIN_HEIGHT + (MAX_HEIGHT - MIN_HEIGHT) * max(1, min(velocity, 127)) / 127


def flame_points(cx: float, base: float, width: float, height: float, t: float, phase: float) -> Tuple[float, ...]:
    """Lobogó lángnyelv sokszöge (simítva rajzolandó): alul széles, a csúcs felé keskenyedik és oldalra leng."""
    def sway(f: float) -> float:
        return width * 0.32 * f * (math.sin(t * 9.0 + phase + f * 3.0) + 0.4 * math.sin(t * 17.0 + 2 * phase))

    half = width / 2
    left, right = [(cx - half, base)], [(cx + half, base)]
    for f in SIDE_POINTS:
        profile = (1 - f) ** 0.75 * (1 + 0.25 * math.sin(math.pi * f))
        y = base - height * f
        left.append((cx - half * profile + sway(f), y))
        right.append((cx + half * profile + sway(f), y))
    tip = (cx + sway(1.0), base - height)
    pts = left + [tip] + right[::-1]
    return tuple(c for p in pts for c in p)


class Visualizer:
    def __init__(self, clock: Callable[[], float] = time.monotonic, seed: int = 7):
        self._clock = clock
        self._rng = random.Random(seed)
        self.flames: List[_Flame] = []
        self.embers: List[_Ember] = []
        self._sounding: Dict[int, _Flame] = {}
        self._last_frame: Optional[float] = None

    @property
    def active(self) -> bool:
        return bool(self.flames or self.embers)

    def clear(self) -> None:
        self.flames.clear()
        self.embers.clear()
        self._sounding.clear()
        self._last_frame = None

    def note_on(self, note: int, velocity: int = 100, t: Optional[float] = None) -> None:
        now = self._clock() if t is None else t
        if note in self._sounding:          # újraindítás: az előző láng kialszik, új csap fel
            self._sounding[note].end = now
        flame = _Flame(note, velocity, now, self._rng.uniform(0, 2 * math.pi))
        self.flames.append(flame)
        self._sounding[note] = flame
        for _ in range(EMBER_BURST):
            self._spawn_ember(note, now, burst=True)
        self._enforce_caps()

    def note_off(self, note: int, t: Optional[float] = None) -> None:
        flame = self._sounding.pop(note, None)
        if flame is not None:
            flame.end = self._clock() if t is None else t

    def _spawn_ember(self, note: int, now: float, burst: bool = False) -> None:
        r = self._rng
        self.embers.append(_Ember(
            note, now, r.uniform(-0.35, 0.35), r.uniform(-40, 40) if burst else r.uniform(-12, 12),
            r.uniform(-150, -95) if burst else r.uniform(-110, -60), r.uniform(1.2, 2.4), r.uniform(0, 2 * math.pi),
        ))

    def _enforce_caps(self) -> None:
        if len(self.flames) > MAX_FLAMES:
            # a kialvó lángok mennek először; szóló hang csak végső esetben
            ended = [f for f in self.flames if f.end is not None]
            drop = set(map(id, ended[: len(self.flames) - MAX_FLAMES]))
            self.flames = [f for f in self.flames if id(f) not in drop]
            while len(self.flames) > MAX_FLAMES:
                old = self.flames.pop(0)
                if self._sounding.get(old.note) is old:
                    del self._sounding[old.note]
        if len(self.embers) > MAX_EMBERS:
            self.embers = self.embers[-MAX_EMBERS:]

    def frame(
        self, now: float, width: float, height: float, key_span: Callable[[int], Optional[Tuple[float, float, bool]]],
    ) -> List[Shape]:
        """A pillanatnyi alakzatok rétegenként hátulról előre (fényudvar, parázs, láng, mag),
        közben a kialudt elemek törlése és az új parázs kibocsátása.

        `key_span(note)` → (x0, x1, fekete) a billentyű vízszintes helye, vagy None.
        """
        dt = 0.0 if self._last_frame is None else min(max(now - self._last_frame, 0.0), 0.1)
        self._last_frame = now
        halos: List[Shape] = []
        bodies: List[Shape] = []
        cores: List[Shape] = []
        alive = []
        for fl in self.flames:
            span = key_span(fl.note)
            grow = min(max((now - fl.start) / ATTACK, 0.0), 1.0)
            fade = 1.0 if fl.end is None else 1.0 - (now - fl.end) / FADE
            intensity = _base_intensity(fl.velocity) * fade
            if span is None or fade <= 0 or intensity < MIN_INTENSITY:
                continue
            alive.append(fl)
            x0, x1, black = span
            cx = (x0 + x1) / 2
            flicker = 1 + 0.12 * math.sin(now * 13.0 + fl.phase) + 0.06 * math.sin(now * 23.0 + 2 * fl.phase)
            h = height * _height_ratio(fl.velocity) * grow * flicker * (0.35 + 0.65 * fade)
            w = (x1 - x0) * WIDTH_FACTOR * (0.6 + 0.4 * fade)
            for spread, level in zip(HALO_WIDTH, HALO_LEVEL):
                hw = w * spread / 2
                top = height - h * (0.45 + 0.22 * spread)
                halos.append(Shape("halo", (cx - hw, top, cx + hw, height + h * 0.3), intensity * level, black))
            bodies.append(Shape("flame", flame_points(cx, height, w, h, now, fl.phase), intensity, black))
            cores.append(Shape("core", flame_points(cx, height, w * CORE_WIDTH, h * CORE_HEIGHT, now, fl.phase + 0.6),
                               min(1.0, intensity * 1.1), black))
            if fl.end is None and dt:
                fl.carry += EMBER_RATE * dt
                while fl.carry >= 1.0:
                    fl.carry -= 1.0
                    self._spawn_ember(fl.note, now)
        self.flames = alive
        self._enforce_caps()

        sparks: List[Shape] = []
        live = []
        for e in self.embers:
            age = now - e.start
            span = key_span(e.note)
            if age > EMBER_LIFE or span is None:
                continue
            x0, x1, black = span
            cx = (x0 + x1) / 2 + e.dx * (x1 - x0) + e.vx * age + 4 * math.sin(age * 7 + e.phase)
            cy = height + e.vy * age
            if cy < -4:
                continue
            live.append(e)
            r = e.size * (1 - 0.4 * age / EMBER_LIFE)
            sparks.append(Shape("ember", (cx - r, cy - r, cx + r, cy + r), 1.0 - age / EMBER_LIFE, black))
        self.embers = live
        return halos + sparks + bodies + cores  # a parázs a láng mögött: csak a csúcs fölött látszik
