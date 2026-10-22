"""Természeti effektek: cseresznyeszirom, falevél, gőz, por, buborék, hópehely, csillag."""

import math

from synth_mido.fx.effects.base import NoteEffect, Particle, Shape, rotated, strength
from synth_mido.skins.palette import mix


def _fade_out(age: float, life: float, tail: float = 0.4) -> float:
    """1, majd az élet utolsó `tail` részében 0-ig halványul."""
    rest = 1.0 - age / life
    return min(1.0, rest / tail)


def _key_glow(v, x0, x1, black, height, fade, out, role="glow", level=0.35, spread=2.4):
    """Lapos, halvány fényfolt a billentyű tövénél, amíg a hang szól (mintha a padlót világítaná meg)."""
    cx, w = (x0 + x1) / 2, (x1 - x0) * spread
    out[role].append(Shape(role, (cx - w / 2, height - w * 0.22, cx + w / 2, height + w * 0.22),
                           strength(v.velocity) * fade * level, black))


# --- sodródó szirmok és levelek ---------------------------------------------------------------

PETAL = ((-0.25, -1.0), (0.0, -0.78), (0.25, -1.0), (1.0, -0.2), (0.4, 0.8), (0.0, 1.0), (-0.4, 0.8), (-1.0, -0.2))
LEAF = ((0.0, -1.0), (0.42, -0.25), (0.3, 0.5), (0.0, 1.0), (-0.3, 0.5), (-0.42, -0.25))


class Petals(NoteEffect):
    """Cseresznyeszirmok: a billentyűkről lassan elszállnak, közben imbolyognak és pörögnek (Sakura)."""

    id = "petals"
    LAYERS = ("glow", "petal_light", "petal")
    KINDS = {"glow": "oval", "petal_light": "poly", "petal": "poly"}
    SMOOTH = ("petal_light", "petal")
    SHAPE = PETAL
    RELEASE = 0.4
    BURST = 3
    RATE = 2.6
    LIFE = 3.2
    MAX_PARTICLES = 60
    SIZE = (3.5, 6.0)            # px — a szirom fél hossza
    WIND = (14.0, 42.0)          # px / mp — a szél jobbra viszi
    LIFT = (-48.0, -22.0)        # px / mp — lassan emelkedik

    def colors(self, p, dark):
        if dark:
            return {"glow": (p["sun_bottom"], p["accent2"]), "petal": (p["sun_mid"], p["sun_bottom"]),
                    "petal_light": (mix(p["sun_top"], "#ffffff", 0.25), p["sun_top"])}
        return {"glow": (p["sun_mid"], p["accent2"]), "petal": (p["sun_bottom"], p["accent"]),
                "petal_light": (p["sun_mid"], p["sun_bottom"])}

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        _key_glow(v, x0, x1, black, height, fade, out, level=0.25)

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.uniform(-0.4, 0.4), vx=r.uniform(*self.WIND), vy=r.uniform(*self.LIFT),
                        size=r.uniform(*self.SIZE), sway=r.uniform(5, 12), freq=r.uniform(1.4, 2.6),
                        phase=r.uniform(0, 2 * math.pi), spin=r.uniform(-2.5, 2.5), flip=r.uniform(1.5, 3.5),
                        role=self.LAYERS[1 + r.randrange(len(self.LAYERS) - 1)], strength=strength(v.velocity))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        cx = (x0 + x1) / 2 + pt.dx * (x1 - x0) + pt.vx * age + pt.sway * math.sin(age * pt.freq + pt.phase)
        cy = height - 4 + pt.vy * age
        if cy < -10 or cx > width + 10:
            return False
        flip = 0.35 + 0.65 * abs(math.cos(age * pt.flip + pt.phase))     # pörgés: a szirom elfordul
        pts = [(x * pt.size * flip, y * pt.size) for x, y in self.SHAPE]
        intensity = pt.strength * _fade_out(age, self.LIFE)
        out[pt.role].append(Shape(pt.role, rotated(cx, cy, pts, pt.phase + age * pt.spin), intensity, black))
        return True


class Leaves(Petals):
    """Falevelek: zöld és arany levelek sodródnak el a billentyűkről (Forest, Safari)."""

    id = "leaves"
    LAYERS = ("glow", "leaf_gold", "leaf")
    KINDS = {"glow": "oval", "leaf_gold": "poly", "leaf": "poly"}
    SMOOTH = ("leaf_gold", "leaf")
    SHAPE = LEAF
    SIZE = (4.5, 7.5)
    WIND = (-30.0, 30.0)
    LIFT = (-55.0, -28.0)

    def colors(self, p, dark):
        return {"glow": (p["accent2"], p["sun_mid"]), "leaf": (p["accent2"], mix(p["accent2"], p["sun_bottom"], 0.4)),
                "leaf_gold": (p["sun_mid"], p["sun_bottom"])}


# --- gőz és por ---------------------------------------------------------------------------------

class Steam(NoteEffect):
    """Gőzpamacsok: lenyomáskor „pfff” — sűrű, gyorsan táguló gőz, amíg szól, folyamatos pára (Steampunk)."""

    id = "steam"
    LAYERS = ("puff", "puff_core")
    KINDS = {"puff": "oval", "puff_core": "oval"}
    RELEASE = 0.2
    BURST = 6
    RATE = 6.0
    LIFE = 1.7
    MAX_PARTICLES = 80
    RISE = (-75.0, -40.0)
    DRIFT = (-14.0, 14.0)
    GROWTH = 13.0               # px — ennyivel nő a pamacs sugara élete során
    LEVEL = 0.75

    def colors(self, p, dark):
        steam = mix(p["fg"], "#ffffff", 0.55) if dark else mix(p["muted"], p["fg"], 0.3)
        return {"puff": (steam, mix(steam, p["accent2"], 0.25)), "puff_core": (mix(steam, "#ffffff", 0.4), steam)}

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.uniform(-0.3, 0.3), vx=r.uniform(*self.DRIFT) * (1.8 if burst else 1),
                        vy=r.uniform(*self.RISE) * (1.4 if burst else 1), r0=r.uniform(2.0, 4.0),
                        phase=r.uniform(0, 2 * math.pi), strength=strength(v.velocity))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        k = age / self.LIFE
        slow = 1 - 0.45 * k                          # a pára lassul, ahogy szétterül
        cx = (x0 + x1) / 2 + pt.dx * (x1 - x0) + pt.vx * age * slow + 3 * math.sin(age * 3 + pt.phase)
        cy = height - 2 + pt.vy * age * slow
        r = pt.r0 + self.GROWTH * math.sqrt(k)
        if cy + r < 0:
            return False
        level = pt.strength * self.LEVEL * (1 - k) ** 1.3
        out["puff"].append(Shape("puff", (cx - r, cy - r * 0.85, cx + r, cy + r * 0.85), level, black))
        if k < 0.5:
            rc = r * 0.5
            out["puff_core"].append(Shape("puff_core", (cx - rc, cy - rc, cx + rc, cy + rc), level * 0.8, black))
        return True


class Dust(Steam):
    """Homokpor: a szél oldalra fújja a felvert port (Desert)."""

    id = "dust"
    BURST = 5
    RATE = 5.0
    LIFE = 2.0
    RISE = (-40.0, -18.0)
    DRIFT = (25.0, 70.0)
    GROWTH = 9.0
    LEVEL = 0.6

    def colors(self, p, dark):
        return {"puff": (p["sun_mid"], p["sun_bottom"]), "puff_core": (p["sun_top"], p["sun_mid"])}


# --- buborék, hó, csillag -------------------------------------------------------------------------

class Bubbles(NoteEffect):
    """Buborékok: imbolyogva szállnak fel, egy csillanással (Ocean)."""

    id = "bubbles"
    LAYERS = ("glow", "bubble", "shine")
    KINDS = {"glow": "oval", "bubble": "ring", "shine": "oval"}
    RELEASE = 0.3
    BURST = 4
    RATE = 4.0
    LIFE = 2.2
    MAX_PARTICLES = 50

    def colors(self, p, dark):
        return {"glow": (p["accent2"], p["accent"]), "bubble": (p["accent2"], mix(p["accent2"], p["accent"], 0.5)),
                "shine": (mix(p["accent2"], "#ffffff", 0.7), "#ffffff")}

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        _key_glow(v, x0, x1, black, height, fade, out, level=0.22)

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.uniform(-0.35, 0.35), vy=r.uniform(-85, -45), r0=r.uniform(1.8, 4.5),
                        wobble=r.uniform(3, 7), phase=r.uniform(0, 2 * math.pi), strength=strength(v.velocity))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        cx = (x0 + x1) / 2 + pt.dx * (x1 - x0) + pt.wobble * math.sin(age * 5 + pt.phase)
        cy = height - 3 + pt.vy * age
        r = pt.r0 * (1 + 0.5 * age / self.LIFE)
        if cy + r < 0:
            return False
        level = pt.strength * _fade_out(age, self.LIFE, 0.25)
        out["bubble"].append(Shape("bubble", (cx - r, cy - r, cx + r, cy + r), level, black))
        s = max(r * 0.28, 0.8)
        out["shine"].append(Shape("shine", (cx - r * 0.45 - s, cy - r * 0.45 - s, cx - r * 0.45 + s,
                                            cy - r * 0.45 + s), level, black))
        return True


class Snow(NoteEffect):
    """Hópelyhek: lassan szállnak és csillámlanak (Arctic)."""

    id = "snow"
    LAYERS = ("glow", "dot", "flake")
    KINDS = {"glow": "oval", "dot": "oval", "flake": "text"}
    FONT_SIZE_MAX = 14
    TEXT_SAMPLE = "❄"
    TEXT_SIZES = (8, 10, 12, 14)
    RELEASE = 0.4
    BURST = 3
    RATE = 3.0
    LIFE = 3.0
    MAX_PARTICLES = 50

    def colors(self, p, dark):
        snow = "#ffffff" if dark else mix(p["accent2"], p["fg"], 0.3)
        return {"glow": (p["accent2"], p["accent"]), "dot": (snow, p["accent2"]), "flake": (snow, p["accent2"])}

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        _key_glow(v, x0, x1, black, height, fade, out, level=0.2)

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.uniform(-0.5, 0.5), vx=r.uniform(-10, 10), vy=r.uniform(-45, -18),
                        size=r.choice(self.TEXT_SIZES), flake=r.random() < 0.55, phase=r.uniform(0, 2 * math.pi),
                        strength=strength(v.velocity))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        cx = (x0 + x1) / 2 + pt.dx * (x1 - x0) + pt.vx * age + 6 * math.sin(age * 1.8 + pt.phase)
        cy = height - 6 + pt.vy * age
        if cy < -8:
            return False
        twinkle = 0.75 + 0.25 * math.sin(age * 9 + pt.phase)
        level = pt.strength * twinkle * _fade_out(age, self.LIFE)
        if pt.flake:
            out["flake"].append(Shape("flake", (cx, cy), level, black, text="❄", size=pt.size))
        else:
            r = pt.size / 7
            out["dot"].append(Shape("dot", (cx - r, cy - r, cx + r, cy + r), level, black))
        return True


STAR = tuple((math.cos(a) * rad, math.sin(a) * rad)
             for i in range(8) for a, rad in [(i * math.pi / 4 - math.pi / 2, 1.0 if i % 2 == 0 else 0.32)])


class Stars(NoteEffect):
    """Csillagok: forogva lövellnek fel és pislákolnak, a billentyű fölött fénycsóva (Astronaut, Art Deco)."""

    id = "stars"
    LAYERS = ("beam", "star_small", "star")
    KINDS = {"beam": "rect", "star_small": "oval", "star": "poly"}
    RELEASE = 0.35
    BURST = 3
    RATE = 3.5
    LIFE = 1.3
    MAX_PARTICLES = 60

    def colors(self, p, dark):
        return {"beam": (p["accent2"], p["accent"]), "star": (p["sun_top"], p["sun_mid"]),
                "star_small": (mix(p["sun_top"], "#ffffff", 0.4), p["accent2"])}

    def voice_shapes(self, v, now, x0, x1, black, height, fade, out):
        cx, w = (x0 + x1) / 2, (x1 - x0) * 0.15
        grow = min((now - v.start) / 0.15, 1.0)
        out["beam"].append(Shape("beam", (cx - w, height * (1 - 0.7 * grow), cx + w, height),
                                 strength(v.velocity) * fade * 0.3, black))

    def spawn(self, v, now, burst):
        r = self.rng
        return Particle(v.note, now, dx=r.uniform(-0.3, 0.3), vx=r.uniform(-50, 50), vy=r.uniform(-120, -60),
                        size=r.uniform(3.5, 6.5), spin=r.uniform(-4, 4), small=r.random() < 0.4,
                        phase=r.uniform(0, 2 * math.pi), strength=strength(v.velocity))

    def particle_shapes(self, pt, age, x0, x1, black, height, width, out):
        slow = 1 - 0.5 * age / self.LIFE
        cx = (x0 + x1) / 2 + pt.dx * (x1 - x0) + pt.vx * age * slow
        cy = height - 4 + pt.vy * age * slow
        if cy < -8:
            return False
        level = pt.strength * (0.7 + 0.3 * math.sin(age * 14 + pt.phase)) * _fade_out(age, self.LIFE)
        if pt.small:
            r = pt.size * 0.3
            out["star_small"].append(Shape("star_small", (cx - r, cy - r, cx + r, cy + r), level, black))
        else:
            pts = [(x * pt.size, y * pt.size) for x, y in STAR]
            out["star"].append(Shape("star", rotated(cx, cy, pts, age * pt.spin), level, black))
        return True
