"""A hangeffektek közös alapja (Strategy minta) — Tk-tól független.

Minden effekt ugyanazt a felületet adja: `note_on / note_off / clear / active` és
`frame(now, width, height, key_span)` → alakzatok listája rétegenként hátulról előre.
Egy effekt két dologból áll össze:

* **hang (voice)** — amíg a hang szól, és elengedés után `RELEASE` másodpercig a
  billentyű fölött rajzolt alakzatok (`voice_shapes`), pl. láng, neon oszlop, izzás;
* **részecskék** — gyújtáskor `BURST` darab, amíg a hang szól, másodpercenként `RATE`
  darab keletkezik (`spawn`), és saját életük van (`particle_shapes`), pl. szirom, gőz.

Az alakzat szerepe (`role`) mondja meg a rajzolónak a réteget (`LAYERS`), a vászon
elem fajtáját (`KINDS`) és a színt (`colors`); így a felületnek nem kell ismernie az
egyes effekteket. Az elemek száma korlátos (`MAX_VOICES`, `MAX_PARTICLES`).
"""

import math
import random
import time
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

KeySpan = Callable[[int], Optional[Tuple[float, float, bool]]]
MIN_INTENSITY = 0.03


class Shape(NamedTuple):
    role: str                   # szerep: réteg + vászon elem fajta + szín
    points: Tuple[float, ...]   # poly: csúcsok; oval / rect / ring: befoglaló téglalap; text: (x, y)
    intensity: float            # 0..1 — a szín ennyire erős a háttérhez képest
    black: bool                 # fekete billentyűből indult (más árnyalat)
    text: str = ""              # csak "text" fajtánál
    size: float = 0.0           # csak "text" fajtánál: betűméret (pt)


class Voice:
    __slots__ = ("note", "velocity", "start", "end", "phase", "carry")

    def __init__(self, note: int, velocity: int, start: float, phase: float):
        self.note, self.velocity, self.start, self.phase = note, velocity, start, phase
        self.end: Optional[float] = None
        self.carry = 0.0   # részecske kibocsátás tört része képkockák között


class Particle:
    """Egy részecske: a `spawn` tetszőleges mezőket ad neki (dx, vx, vy, size, spin …)."""

    def __init__(self, note: int, start: float, black: bool = False, **fields):
        self.note, self.start, self.black = note, start, black
        self.__dict__.update(fields)


def strength(velocity: int) -> float:
    """Hangerő → 0.5..1 erősség."""
    return 0.5 + 0.5 * max(1, min(velocity, 127)) / 127


def rotated(cx: float, cy: float, pts, angle: float) -> Tuple[float, ...]:
    """Pontok elforgatása (cx, cy) körül, lapított koordinátalistaként."""
    ca, sa = math.cos(angle), math.sin(angle)
    return tuple(v for x, y in pts for v in (cx + x * ca - y * sa, cy + x * sa + y * ca))


class NoteEffect:
    id = ""
    LAYERS: Tuple[str, ...] = ()           # szerepek rajzolási sorrendben
    KINDS: Dict[str, str] = {}             # szerep -> poly | oval | rect | ring | text
    SMOOTH: Tuple[str, ...] = ()           # simított sokszög szerepek
    RELEASE = 0.5                          # mp — elengedés után ennyi ideig rajzolódik a hang
    BURST = 0
    RATE = 0.0
    LIFE = 1.0                             # részecske élettartam (mp)
    MAX_VOICES = 40
    MAX_PARTICLES = 70
    FONT_SIZE_MAX = 0                      # text szerepeknél a legnagyobb betűméret
    TEXT_SAMPLE = ""                       # a text szerepek összes jele (a felület előre betölti a betűtípust)
    TEXT_SIZES: Tuple[int, ...] = ()       # … ezekben a méretekben

    def __init__(self, clock: Callable[[], float] = time.monotonic, seed: int = 7):
        self._clock = clock
        self.rng = random.Random(seed)
        self.voices: List[Voice] = []
        self.particles: List[Particle] = []
        self._sounding: Dict[int, Voice] = {}
        self._last_frame: Optional[float] = None

    # --- színek (a felület hívja) -----------------------------------------------------

    def colors(self, p: dict, dark: bool) -> Dict[str, Tuple[str, str]]:
        """Szerep -> (fehér billentyű szín, fekete billentyű szín) a skin palettájából."""
        return {role: (p["key_white_active"], p["key_black_active"]) for role in self.LAYERS}

    # --- hangok ------------------------------------------------------------------------

    @property
    def active(self) -> bool:
        return bool(self.voices or self.particles)

    def clear(self) -> None:
        self.voices.clear()
        self.particles.clear()
        self._sounding.clear()
        self._last_frame = None

    def note_on(self, note: int, velocity: int = 100, t: Optional[float] = None) -> None:
        now = self._clock() if t is None else t
        if note in self._sounding:          # újraindítás: az előző lecseng, új indul
            self._sounding[note].end = now
        voice = Voice(note, velocity, now, self.rng.uniform(0, 2 * math.pi))
        self.voices.append(voice)
        self._sounding[note] = voice
        for _ in range(self.BURST):
            self.particles.append(self.spawn(voice, now, burst=True))
        self._enforce_caps()

    def note_off(self, note: int, t: Optional[float] = None) -> None:
        voice = self._sounding.pop(note, None)
        if voice is not None:
            voice.end = self._clock() if t is None else t

    def _enforce_caps(self) -> None:
        if len(self.voices) > self.MAX_VOICES:
            # a lecsengők mennek először; szóló hang csak végső esetben
            ended = [v for v in self.voices if v.end is not None]
            drop = set(map(id, ended[: len(self.voices) - self.MAX_VOICES]))
            self.voices = [v for v in self.voices if id(v) not in drop]
            while len(self.voices) > self.MAX_VOICES:
                old = self.voices.pop(0)
                if self._sounding.get(old.note) is old:
                    del self._sounding[old.note]
        if len(self.particles) > self.MAX_PARTICLES:
            self.particles = self.particles[-self.MAX_PARTICLES:]

    # --- az effekt saját része (felülírandó) --------------------------------------------

    def voice_shapes(self, v: Voice, now: float, x0: float, x1: float, black: bool, height: float,
                     fade: float, out: Dict[str, list]) -> None:
        """A hang saját alakzatai (`fade`: 1 amíg szól, elengedés után 1 → 0)."""

    def spawn(self, v: Voice, now: float, burst: bool) -> Particle:
        raise NotImplementedError

    def particle_shapes(self, pt: Particle, age: float, x0: float, x1: float, black: bool, height: float,
                        width: float, out: Dict[str, list]) -> bool:
        """A részecske alakzatai; False, ha már nem látszik (törölhető)."""
        return False

    # --- képkocka ----------------------------------------------------------------------

    def frame(self, now: float, width: float, height: float, key_span: KeySpan) -> List[Shape]:
        dt = 0.0 if self._last_frame is None else min(max(now - self._last_frame, 0.0), 0.1)
        self._last_frame = now
        out: Dict[str, list] = {role: [] for role in self.LAYERS}
        alive = []
        for v in self.voices:
            span = key_span(v.note)
            fade = 1.0 if v.end is None else 1.0 - (now - v.end) / self.RELEASE
            if span is None or fade <= 0:
                continue
            alive.append(v)
            self.voice_shapes(v, now, span[0], span[1], span[2], height, fade, out)
            if v.end is None and dt and self.RATE:
                v.carry += self.RATE * dt
                while v.carry >= 1.0:
                    v.carry -= 1.0
                    self.particles.append(self.spawn(v, now, burst=False))
        self.voices = alive
        self._enforce_caps()

        live = []
        for pt in self.particles:
            age = now - pt.start
            span = key_span(pt.note)
            if age > self.LIFE or span is None:
                continue
            if self.particle_shapes(pt, age, span[0], span[1], span[2], height, width, out):
                live.append(pt)
        self.particles = live
        return [s for role in self.LAYERS for s in out[role] if s.intensity >= MIN_INTENSITY]
