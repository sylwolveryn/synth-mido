"""Neon oszlopok (Synthwave, Classic) és lángok (Volcano)."""

import math

from synth_mido.fx.effects.base import NoteEffect, Particle, Shape, strength
from synth_mido.skins.palette import mix


class NeonBars(NoteEffect):
    """Minden szóló hang neon oszlopot növeszt; elengedéskor leválik, emelkedik és elhalványul, gyújtáskor szikrák."""

    id = "neon"
    LAYERS = ("glow", "bar", "spark")
    KINDS = {"glow": "rect", "bar": "rect", "spark": "oval"}
    RELEASE = 1.6          # a leváló oszlop ennyi idő alatt halványul el
    BURST = 3
    LIFE = 0.4
    MAX_VOICES = 96
    MAX_PARTICLES = 60
    RISE_SPEED = 140.0     # px / mp
    GLOW_PAD = 3.0

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        top = height - (now - v.start) * self.RISE_SPEED
        bottom = height if v.end is None else height - (now - v.end) * self.RISE_SPEED
        if bottom <= 0:
            return
        intensity = strength(v.velocity) * fade
        top = max(top, 0.0)
        if v.end is None:
            g = self.GLOW_PAD
            out["glow"].append(Shape("glow", (x0 - g, top - g, x1 + g, bottom), intensity * 0.35, black))
        out["bar"].append(Shape("bar", (x0, top, x1, bottom), intensity, black))

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.uniform(-0.3, 0.3), vx=r.uniform(-45, 45), vy=r.uniform(-170, -90))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        cx = (x0 + x1) / 2 + pt.dx * (x1 - x0) + pt.vx * age
        cy = height + pt.vy * age
        out["spark"].append(Shape("spark", (cx - 1.5, cy - 1.5, cx + 1.5, cy + 1.5), 1.0 - age / self.LIFE, black))
        return True


def flame_points(cx, base, width, height, t, phase):
    """Lobogó lángnyelv sokszöge (simítva rajzolandó): alul széles, a csúcs felé keskenyedik és oldalra leng."""
    def sway(f):
        return width * 0.32 * f * (math.sin(t * 9.0 + phase + f * 3.0) + 0.4 * math.sin(t * 17.0 + 2 * phase))

    half = width / 2
    left, right = [(cx - half, base)], [(cx + half, base)]
    for f in (0.22, 0.48, 0.74):
        profile = (1 - f) ** 0.75 * (1 + 0.25 * math.sin(math.pi * f))
        y = base - height * f
        left.append((cx - half * profile + sway(f), y))
        right.append((cx + half * profile + sway(f), y))
    pts = left + [(cx + sway(1.0), base - height)] + right[::-1]
    return tuple(c for p in pts for c in p)


class Flames(NoteEffect):
    """Lobogó láng háromrétegű fényudvarral és világos maggal; a csúcsáról parázs száll fel."""

    id = "flames"
    LAYERS = ("halo", "ember", "flame", "core")   # a parázs a láng mögött: csak a csúcs fölött látszik
    KINDS = {"halo": "oval", "ember": "oval", "flame": "poly", "core": "poly"}
    SMOOTH = ("flame", "core")
    RELEASE = 0.55
    ATTACK = 0.08
    BURST = 4
    RATE = 7.0
    LIFE = 0.9
    MAX_VOICES = 40
    MAX_PARTICLES = 70
    MIN_HEIGHT, MAX_HEIGHT = 0.35, 0.95
    WIDTH_FACTOR = 2.1
    HALOS = ((3.0, 0.08), (2.2, 0.15), (1.5, 0.26))   # (szélesség, erősség) kívülről befelé

    def colors(self, p, dark):
        if dark:
            return {"halo": (p["sun_bottom"], p["accent2"]), "flame": (p["sun_mid"], p["sun_bottom"]),
                    "core": (mix(p["sun_top"], "#ffffff", 0.35), p["sun_top"]), "ember": (p["sun_top"], p["sun_mid"])}
        return {"halo": (p["sun_mid"], p["accent2"]), "flame": (p["sun_bottom"], p["accent"]),
                "core": (p["sun_top"], p["sun_mid"]), "ember": (p["sun_bottom"], p["accent"])}

    def flame_size(self, v, now, x0, x1, height, fade):
        grow = min(max((now - v.start) / self.ATTACK, 0.0), 1.0)
        flicker = 1 + 0.12 * math.sin(now * 13.0 + v.phase) + 0.06 * math.sin(now * 23.0 + 2 * v.phase)
        ratio = self.MIN_HEIGHT + (self.MAX_HEIGHT - self.MIN_HEIGHT) * max(1, min(v.velocity, 127)) / 127
        h = height * ratio * grow * flicker * (0.35 + 0.65 * fade)
        w = (x1 - x0) * self.WIDTH_FACTOR * (0.6 + 0.4 * fade)
        return w, h

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        intensity = strength(v.velocity) * fade
        cx = (x0 + x1) / 2
        w, h = self.flame_size(v, now, x0, x1, height, fade)
        for spread, level in self.HALOS:
            hw = w * spread / 2
            top = height - h * (0.45 + 0.22 * spread)
            out["halo"].append(Shape("halo", (cx - hw, top, cx + hw, height + h * 0.3), intensity * level, black))
        out["flame"].append(Shape("flame", flame_points(cx, height, w, h, now, v.phase), intensity, black))
        out["core"].append(Shape("core", flame_points(cx, height, w * 0.45, h * 0.6, now, v.phase + 0.6),
                                 min(1.0, intensity * 1.1), black))

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.uniform(-0.35, 0.35),
                        vx=r.uniform(-40, 40) if burst else r.uniform(-12, 12),
                        vy=r.uniform(-150, -95) if burst else r.uniform(-110, -60),
                        size=r.uniform(1.2, 2.4), phase=r.uniform(0, 2 * math.pi))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        cx = (x0 + x1) / 2 + pt.dx * (x1 - x0) + pt.vx * age + 4 * math.sin(age * 7 + pt.phase)
        cy = height + pt.vy * age
        if cy < -4:
            return False
        r = pt.size * (1 - 0.4 * age / self.LIFE)
        out["ember"].append(Shape("ember", (cx - r, cy - r, cx + r, cy + r), 1.0 - age / self.LIFE, black))
        return True
