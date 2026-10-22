"""Pixelek (Arcade) és felszálló jelek: matematika, római számok, hangjegyek, iránytű csillagok."""

import math

from synth_mido.fx.effects.base import NoteEffect, Particle, Shape, strength
from synth_mido.skins.palette import mix

PIXEL = 6.0   # px — a „képernyő” rácsa


def _snap(v: float) -> float:
    return math.floor(v / PIXEL) * PIXEL


class Pixels(NoteEffect):
    """8 bites pixelek: a hang lépcsőzetes oszlopot épít, pixelkockák ugrálnak fel rácsra illesztve (Arcade)."""

    id = "pixels"
    LAYERS = ("block", "pixel_a", "pixel_b", "pixel_c")
    KINDS = {"block": "rect", "pixel_a": "rect", "pixel_b": "rect", "pixel_c": "rect"}
    RELEASE = 0.3
    BURST = 4
    RATE = 4.0
    LIFE = 1.1
    MAX_VOICES = 24              # egy hang akár 10 kocka: szigorúbb korlát
    MAX_PARTICLES = 60
    STEP = 0.05                  # mp — ennyi időnként nő egy kockát az oszlop

    def colors(self, p, dark):
        return {"block": (p["accent2"], p["accent"]), "pixel_a": (p["accent"], p["accent"]),
                "pixel_b": (p["accent2"], p["accent2"]), "pixel_c": (p["sun_top"], p["sun_top"])}

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        top_blocks = int(2 + 8 * max(1, min(v.velocity, 127)) / 127)
        blocks = min(top_blocks, 1 + int((now - v.start) / self.STEP))
        blocks = max(1, int(blocks * fade + 0.999))
        cx = (x0 + x1) / 2
        bx0 = _snap(cx - PIXEL / 2)
        level = strength(v.velocity) * (0.55 + 0.45 * fade)
        for i in range(blocks):
            y1 = height - i * PIXEL
            out["block"].append(Shape("block", (bx0, y1 - PIXEL + 1, bx0 + PIXEL - 1, y1), level * (1 - 0.06 * i),
                                      black))

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.choice((-1, 0, 1)), vy=r.uniform(-110, -60), hop=r.choice((-1, 1)),
                        role=r.choice(("pixel_a", "pixel_b", "pixel_c")), strength=strength(v.velocity))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        steps = int(age / 0.08)                       # lépcsőzetes mozgás, mint egy régi játékban
        t = steps * 0.08
        x = _snap((x0 + x1) / 2 + pt.dx * PIXEL + pt.hop * PIXEL * (steps // 4))
        y = _snap(height - PIXEL + pt.vy * t)
        if y < -PIXEL:
            return False
        level = pt.strength * (1.0 if age < self.LIFE * 0.6 else 0.5)
        out[pt.role].append(Shape(pt.role, (x, y, x + PIXEL - 1, y + PIXEL - 1), level, black))
        return True


class Glyphs(NoteEffect):
    """Felszálló jelek a billentyűkből; a jelkészletet az alosztály adja."""

    id = "glyphs"
    GLYPHS = "♪"
    LAYERS = ("glow", "glyph")
    KINDS = {"glow": "oval", "glyph": "text"}
    FONT_SIZE_MAX = 18
    RELEASE = 0.4
    BURST = 1
    RATE = 1.6
    LIFE = 1.9
    MAX_PARTICLES = 36
    SIZES = (10, 12, 14, 16, 18)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TEXT_SAMPLE, self.TEXT_SIZES = self.GLYPHS, self.SIZES

    def colors(self, p, dark):
        return {"glow": (p["accent"], p["accent2"]), "glyph": (p["accent2"], p["accent"])}

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        cx, w = (x0 + x1) / 2, (x1 - x0) * 2.2
        out["glow"].append(Shape("glow", (cx - w / 2, height - w * 0.22, cx + w / 2, height + w * 0.22),
                                 strength(v.velocity) * fade * 0.3, black))

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, glyph=r.choice(self.GLYPHS), size=r.choice(self.SIZES),
                        vx=r.uniform(-18, 18), vy=r.uniform(-60, -35), phase=r.uniform(0, 2 * math.pi),
                        strength=strength(v.velocity))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        cx = (x0 + x1) / 2 + pt.vx * age + 5 * math.sin(age * 2.5 + pt.phase)
        cy = height - 10 + pt.vy * age
        if cy < -pt.size:
            return False
        level = pt.strength * min(1.0, (1 - age / self.LIFE) / 0.5)
        out["glyph"].append(Shape("glyph", (cx, cy), level, black, text=pt.glyph, size=pt.size))
        return True


class MathGlyphs(Glyphs):
    id = "math"
    GLYPHS = "π∑√∞±×÷=∫∂"


class RomanGlyphs(Glyphs):
    id = "roman"
    GLYPHS = "ⅠⅡⅢⅣⅤⅥⅩⅬⅭ"

    def colors(self, p, dark):
        return {"glow": (p["sun_mid"], p["accent"]), "glyph": (p["sun_top"], p["sun_mid"])}


class MusicNotes(Glyphs):
    id = "notes"
    GLYPHS = "♪♫♬♩"

    def colors(self, p, dark):
        return {"glow": (p["accent"], p["accent2"]), "glyph": (mix(p["sun_top"], p["accent"], 0.3), p["accent2"])}


class CompassGlyphs(Glyphs):
    id = "compass"
    GLYPHS = "✦✧★☆✶"
    SIZES = (9, 11, 13, 15)

    def colors(self, p, dark):
        return {"glow": (p["accent2"], p["sun_mid"]), "glyph": (p["sun_mid"], p["accent2"])}
