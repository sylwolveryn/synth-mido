"""Hangszínszabályzó animációk (Strategy + Registry minta).

Minden animáció ugyanazt a felületet adja: `render(spectrum, width, height)` →
alakzatok listája szerepkörrel ("low" / "mid" / "high" / "peak" / "line" / "grid")
és erősséggel. A színt a felület adja a skinből, így minden animáció minden skinnel
működik; a modell Tk nélkül tesztelhető.
"""

import math
from typing import Dict, List, NamedTuple, Tuple, Type


class Shape(NamedTuple):
    kind: str            # "rect" | "line" | "oval" | "poly"
    coords: Tuple[float, ...]
    role: str            # színszerep
    intensity: float = 1.0
    width: float = 1.0   # vonalvastagság (line / poly körvonal)


def level_role(fraction: float) -> str:
    """A klasszikus Winamp színezés: alul "low", középen "mid", fent "high"."""
    if fraction < 0.55:
        return "low"
    if fraction < 0.82:
        return "mid"
    return "high"


class Animation:
    id = ""
    label = ""
    led_rows = 0   # > 0: statikus LED rács a sávokon (a felület rajzolja egyszer)

    def render(self, spectrum, width: float, height: float) -> List[Shape]:
        raise NotImplementedError


class ClassicBars(Animation):
    """Klasszikus Winamp: LED szegmenses oszlopok, alul zöld (low) → sárga (mid) → piros (high), lehulló csúcsok."""

    id, label, led_rows = "bars", "Klasszikus oszlopok", 18

    def render(self, s, w, h):
        out, bw = [], w / s.bands
        pad = max(1.0, bw * 0.12)
        for i, level in enumerate(s.levels):
            x0, x1 = i * bw + pad, (i + 1) * bw - pad
            # a sáv három szín szakaszból áll (low / mid / high)
            for lo, hi, role in ((0.0, 0.55, "low"), (0.55, 0.82, "mid"), (0.82, 1.0, "high")):
                if level > lo:
                    y0 = h * (1 - min(level, hi))
                    out.append(Shape("rect", (x0, y0, x1, h * (1 - lo)), role))
            peak_y = h * (1 - s.peaks[i])
            out.append(Shape("rect", (x0, peak_y - 3, x1, peak_y), "peak"))
        return out


class MirrorBars(Animation):
    """Tükrözött oszlopok a középvonalhoz képest."""

    id, label = "mirror", "Tükrözött oszlopok"

    def render(self, s, w, h):
        out, bw, mid = [], w / s.bands, h / 2
        for i, level in enumerate(s.levels):
            x0, x1 = i * bw + 1.5, (i + 1) * bw - 1.5
            half = level * (h / 2 - 4)
            role = level_role(level)
            out.append(Shape("rect", (x0, mid - half, x1, mid), role, 0.55 + 0.45 * level))
            out.append(Shape("rect", (x0, mid, x1, mid + half), role, 0.35 + 0.35 * level))
            pk = s.peaks[i] * (h / 2 - 4)
            out.append(Shape("rect", (x0, mid - pk - 2, x1, mid - pk), "peak"))
            out.append(Shape("rect", (x0, mid + pk, x1, mid + pk + 2), "peak", 0.6))
        out.append(Shape("line", (0, mid, w, mid), "grid", 0.6))
        return out


class Oscilloscope(Animation):
    """Oszcilloszkóp: a szóló hangok összegzett hullámformája."""

    id, label = "scope", "Oszcilloszkóp"

    def render(self, s, w, h):
        samples = max(32, int(w / 5))
        wave = s.wave(samples)
        mid, amp = h / 2, h * 0.42
        coords = []
        for i, v in enumerate(wave):
            coords += [w * i / (samples - 1), mid - v * amp]
        loud = max(s.levels) if s.levels else 0
        return [
            Shape("line", (0, mid, w, mid), "grid", 0.5),
            Shape("line", tuple(coords), "line", 0.35, width=6),   # ragyogás
            Shape("line", tuple(coords), "line", 0.6 + 0.4 * loud, width=2),
        ]


class RadialBars(Animation):
    """Kör alakú sugaras oszlopok, középen pulzáló kör."""

    id, label = "radial", "Kör spektrum"

    def render(self, s, w, h):
        cx, cy = w / 2, h / 2
        radius = min(w, h) * 0.18
        reach = min(w, h) * 0.3
        loud = sum(s.levels) / max(len(s.levels), 1)
        pulse = radius * (1 + loud * 0.3)
        out = [Shape("oval", (cx - pulse, cy - pulse, cx + pulse, cy + pulse), "mid", 0.25 + 0.5 * loud)]
        n = s.bands * 2  # körbe tükrözve
        thick = max(2.0, 2 * math.pi * radius / n * 0.55)
        for k in range(n):
            i = k if k < s.bands else n - 1 - k
            a = 2 * math.pi * k / n - math.pi / 2
            r1 = radius + 3 + s.levels[i] * reach
            out.append(Shape("line", (cx + math.cos(a) * (radius + 3), cy + math.sin(a) * (radius + 3),
                                      cx + math.cos(a) * r1, cy + math.sin(a) * r1),
                             level_role(s.levels[i]), 0.5 + 0.5 * s.levels[i], width=thick))
            rp = radius + 3 + s.peaks[i] * reach + 3
            out.append(Shape("oval", (cx + math.cos(a) * rp - 1.5, cy + math.sin(a) * rp - 1.5,
                                      cx + math.cos(a) * rp + 1.5, cy + math.sin(a) * rp + 1.5), "peak"))
        return out


class Fire(Animation):
    """Tűz / plazma: lobogó lángnyelvek a sávok fölött."""

    id, label = "fire", "Tűz"

    def render(self, s, w, h):
        out, bw, t = [], w / s.bands, s.time
        layers = (("high", 1.0, 0.95), ("mid", 0.72, 0.85), ("low", 0.45, 0.75))
        for i, level in enumerate(s.levels):
            if level < 0.01:
                continue
            cx = (i + 0.5) * bw
            for k, (role, size, inten) in enumerate(layers):
                flicker = 0.8 + 0.2 * math.sin(t * 9 + i * 1.7 + k * 2.3) * math.sin(t * 4.3 + i * 0.9)
                fh = level * h * size * flicker
                half = bw * (0.55 + 0.2 * size)
                sway = math.sin(t * 6 + i + k) * bw * 0.25
                xs = [cx - half, cx + half, cx + half * 0.4 + sway, cx + sway, cx - half * 0.4 + sway]
                xs = [min(max(x, 0.0), w) for x in xs]
                ys = [h, h, h - fh * 0.55, h - fh, h - fh * 0.55]
                out.append(Shape("poly", tuple(v for xy in zip(xs, ys) for v in xy), role,
                                 inten * (0.6 + 0.4 * level)))
        return out


class Area(Animation):
    """Kitöltött spektrum görbe csúcspontokkal."""

    id, label = "area", "Spektrum görbe"

    def render(self, s, w, h):
        bw = w / max(s.bands - 1, 1)
        top = [(i * bw, h - 2 - lv * (h - 8)) for i, lv in enumerate(s.levels)]
        poly = [0, h] + [v for pt in top for v in pt] + [w, h]
        out = [Shape("poly", tuple(poly), "low", 0.55)]
        out.append(Shape("line", tuple(v for pt in top for v in pt), "line", 1.0, width=2))
        for i, pk in enumerate(s.peaks):
            x, y = i * bw, h - 2 - pk * (h - 8)
            out.append(Shape("oval", (x - 2, y - 2, x + 2, y + 2), "peak"))
        return out


ANIMATIONS: Dict[str, Type[Animation]] = {}
for _cls in (ClassicBars, MirrorBars, Oscilloscope, RadialBars, Fire, Area):
    ANIMATIONS[_cls.id] = _cls
DEFAULT = ClassicBars.id


def create(animation_id: str) -> Animation:
    return ANIMATIONS.get(animation_id, ANIMATIONS[DEFAULT])()
