"""Hangszer illusztrációk: minden General MIDI hangszercsaládhoz egy cuki állat a hangszerével.

A General MIDI 128 hangszere 16 nyolcas családba tartozik (zongorák, orgonák, gitárok …);
minden család saját, előre megrajzolt állatot és hangszert kap (pl. fuvola → madárka
fuvolával). A rajz csak vászon primitívekből áll (nincs képfájl), egy 100 × 100-as
egységnyi dobozban készül, és tetszőleges méretre skálázható. A vászon bármi lehet,
aminek `create_oval / create_rectangle / create_polygon / create_line / create_arc`
metódusa van (Tk Canvas, tesztben hamis vászon).
"""

import math
from typing import Dict, List, NamedTuple, Tuple

from synth_mido.skins.palette import mix


class Family(NamedTuple):
    id: str          # a család azonosítója (fordítási kulcs is: art.<id>)
    animal: str
    instrument: str


# programszám // 8 szerinti sorrendben (General MIDI)
FAMILIES: Tuple[Family, ...] = (
    Family("piano", "cat", "piano"),
    Family("chromatic", "penguin", "xylophone"),
    Family("organ", "owl", "organ"),
    Family("guitar", "fox", "guitar"),
    Family("bass", "bear", "bass"),
    Family("strings", "rabbit", "violin"),
    Family("ensemble", "frog", "choir"),
    Family("brass", "elephant", "trumpet"),
    Family("reed", "raccoon", "sax"),
    Family("pipe", "bird", "flute"),
    Family("synth_lead", "dog", "keytar"),
    Family("synth_pad", "koala", "pad"),
    Family("synth_fx", "octopus", "knobs"),
    Family("ethnic", "panda", "banjo"),
    Family("percussive", "monkey", "drum"),
    Family("sound_fx", "parrot", "megaphone"),
)


def family_of(program: int) -> Family:
    """A hangszer (0–127) családja; tartományon kívül az első (zongora)."""
    return FAMILIES[program // 8] if 0 <= program <= 127 else FAMILIES[0]


# --- állatok: szőrszín (fő, világos, sötét) és jellegzetességek ------------------------

class Animal(NamedTuple):
    fur: str
    light: str
    dark: str
    ears: str             # pointy | round | long | floppy | tufts | big_round | side | none
    face: Tuple[str, ...] = ()   # whiskers, beak, trunk, mask, patches, muzzle, frog, crest, tentacles


ANIMALS: Dict[str, Animal] = {
    "cat": Animal("#f2a65a", "#fde3c8", "#b5651d", "pointy", ("whiskers", "muzzle")),
    "penguin": Animal("#2f3542", "#f5f6fa", "#1e222b", "none", ("beak", "belly")),
    "owl": Animal("#a47551", "#f3e1c7", "#6b4423", "tufts", ("owl_eyes", "beak")),
    "fox": Animal("#f07f2c", "#fff4e6", "#a8481a", "pointy", ("muzzle", "fox_cheeks")),
    "bear": Animal("#9c6b43", "#e8c9a7", "#5e3b22", "round", ("muzzle",)),
    "rabbit": Animal("#e9e4f0", "#ffffff", "#b9a9c9", "long", ("muzzle", "whiskers")),
    "frog": Animal("#69c06b", "#d8f3c4", "#2f7d32", "none", ("frog",)),
    "elephant": Animal("#a3b1c2", "#dfe6ee", "#6b7a8f", "big_round", ("trunk",)),
    "raccoon": Animal("#9aa0a8", "#eceff1", "#3b3f45", "round", ("mask", "muzzle")),
    "bird": Animal("#5aa9e6", "#fff3b0", "#2b6cb0", "none", ("beak", "crest", "belly")),
    "dog": Animal("#d9a066", "#fbe7cf", "#8a5a2b", "floppy", ("muzzle",)),
    "koala": Animal("#a8aeb8", "#eef0f3", "#5f6670", "big_round", ("koala_nose",)),
    "octopus": Animal("#e46f9a", "#ffd1e1", "#a23b63", "none", ("tentacles",)),
    "panda": Animal("#f7f7f7", "#ffffff", "#25262b", "round", ("patches", "muzzle")),
    "monkey": Animal("#9b6a3f", "#f1d1a8", "#5c3a1e", "side", ("monkey_face",)),
    "parrot": Animal("#3fb950", "#ffd33d", "#d1242f", "none", ("beak", "crest", "belly")),
}


class Pen:
    """Egységnyi (0–100) koordináták → vászon koordináták; minden alakzat körvonalat kap."""

    def __init__(self, canvas, x: float, y: float, size: float, outline: str, tag: str):
        self.c, self.x, self.y, self.s = canvas, x, y, size / 100
        self.outline, self.tag = outline, tag

    def _pts(self, points):
        return [v for px, py in points for v in (self.x + px * self.s, self.y + py * self.s)]

    def _w(self, width):
        return max(1.0, width * self.s)

    def oval(self, x0, y0, x1, y1, fill, width=1.2, outline=True):
        return self.c.create_oval(*self._pts([(x0, y0), (x1, y1)]), fill=fill,
                                  outline=self.outline if outline else "", width=self._w(width), tags=(self.tag,))

    def circle(self, cx, cy, r, fill, **kw):
        return self.oval(cx - r, cy - r, cx + r, cy + r, fill, **kw)

    def rect(self, x0, y0, x1, y1, fill, width=1.2, outline=True):
        return self.c.create_rectangle(*self._pts([(x0, y0), (x1, y1)]), fill=fill,
                                       outline=self.outline if outline else "", width=self._w(width), tags=(self.tag,))

    def poly(self, points, fill, smooth=False, width=1.2, outline=True):
        return self.c.create_polygon(*self._pts(points), fill=fill, smooth=smooth,
                                     outline=self.outline if outline else "", width=self._w(width), tags=(self.tag,))

    def line(self, points, fill=None, width=1.5, smooth=False):
        return self.c.create_line(*self._pts(points), fill=fill or self.outline, width=self._w(width),
                                  smooth=smooth, capstyle="round", tags=(self.tag,))

    def arc(self, x0, y0, x1, y1, start, extent, fill=None, width=1.5):
        return self.c.create_arc(*self._pts([(x0, y0), (x1, y1)]), start=start, extent=extent, style="arc",
                                 outline=fill or self.outline, width=self._w(width), tags=(self.tag,))


# --- az állat részei ---------------------------------------------------------------------

HEAD = (40.0, 36.0, 19.0)     # a fej középpontja és sugara
BODY = (22.0, 52.0, 58.0, 98.0)


def _ears(pen: Pen, a: Animal, inner: str):
    cx, cy, r = HEAD
    if a.ears == "pointy":
        for side in (-1, 1):
            pen.poly([(cx + side * 6, cy - r + 3), (cx + side * 17, cy - r - 9), (cx + side * 18, cy - 4)], a.fur)
            pen.poly([(cx + side * 9, cy - r + 3), (cx + side * 15.5, cy - r - 4), (cx + side * 15.5, cy - 7)], inner,
                     outline=False)
    elif a.ears == "round":
        for side in (-1, 1):
            pen.circle(cx + side * 14, cy - r + 3, 6.5, a.dark if "patches" in a.face else a.fur)
            pen.circle(cx + side * 14, cy - r + 3, 3.2, inner, outline=False)
    elif a.ears == "big_round":
        for side in (-1, 1):
            pen.circle(cx + side * 19, cy - 6, 11, a.fur)
            pen.circle(cx + side * 19, cy - 6, 6.5, a.light, outline=False)
    elif a.ears == "long":
        for side in (-1, 1):
            pen.oval(cx + side * 9 - 5, cy - r - 16, cx + side * 9 + 5, cy - r + 6, a.fur)
            pen.oval(cx + side * 9 - 2.3, cy - r - 12, cx + side * 9 + 2.3, cy - r + 3, inner, outline=False)
    elif a.ears == "floppy":
        for side in (-1, 1):
            pen.oval(cx + side * 17 - 6, cy - 14, cx + side * 17 + 6, cy + 8, a.dark)
    elif a.ears == "tufts":
        for side in (-1, 1):
            pen.poly([(cx + side * 8, cy - r + 2), (cx + side * 16, cy - r - 8), (cx + side * 17, cy - r + 6)], a.dark)
    elif a.ears == "side":
        for side in (-1, 1):
            pen.circle(cx + side * 20, cy + 1, 6.5, a.fur)
            pen.circle(cx + side * 20, cy + 1, 3.5, a.light, outline=False)


def _eyes(pen: Pen, a: Animal, eye_y: float, spread: float = 7.0, big: bool = False):
    cx = HEAD[0]
    for side in (-1, 1):
        ex = cx + side * spread
        if big:
            pen.circle(ex, eye_y, 6.2, "#ffffff")
            pen.circle(ex, eye_y, 3.6, "#2b2118", outline=False)
            pen.circle(ex + 1.2, eye_y - 1.3, 1.2, "#ffffff", outline=False)
        else:
            pen.circle(ex, eye_y, 2.6, "#2b2118", outline=False)
            pen.circle(ex + 0.9, eye_y - 1.0, 0.9, "#ffffff", outline=False)


def _head(pen: Pen, a: Animal, cheek: str):
    cx, cy, r = HEAD
    inner = mix(a.light, cheek, 0.35)
    _ears(pen, a, inner)
    if "frog" in a.face:
        for side in (-1, 1):  # a béka szeme a feje tetején ül
            pen.circle(cx + side * 9, cy - r + 2, 7, a.fur)
        pen.oval(cx - r - 2, cy - r + 4, cx + r + 2, cy + r - 2, a.fur)
        for side in (-1, 1):
            pen.circle(cx + side * 9, cy - r + 2, 4.5, "#ffffff")
            pen.circle(cx + side * 9, cy - r + 2.5, 2.4, "#2b2118", outline=False)
        pen.arc(cx - 11, cy - 6, cx + 11, cy + 8, 200, 140, width=1.6)
        for side in (-1, 1):
            pen.circle(cx + side * 14, cy + 2, 3, cheek, outline=False)
        return
    pen.circle(cx, cy, r, a.fur)
    if "owl_eyes" in a.face:
        pen.oval(cx - r + 3, cy - 12, cx + r - 3, cy + 12, a.light, outline=False)
        _eyes(pen, a, cy - 2, spread=7.5, big=True)
    elif "patches" in a.face:
        for side in (-1, 1):
            pen.oval(cx + side * 8 - 5, cy - 8, cx + side * 8 + 5, cy + 3, a.dark, outline=False)
        for side in (-1, 1):
            pen.circle(cx + side * 8, cy - 3, 2.3, "#ffffff", outline=False)
            pen.circle(cx + side * 8, cy - 3, 1.2, "#111111", outline=False)
    elif "mask" in a.face:
        pen.oval(cx - r + 2, cy - 9, cx + r - 2, cy + 2, a.dark, outline=False)
        for side in (-1, 1):
            pen.circle(cx + side * 7, cy - 4, 2.7, "#ffffff", outline=False)
            pen.circle(cx + side * 7, cy - 4, 1.4, "#111111", outline=False)
    elif "monkey_face" in a.face:
        pen.oval(cx - 13, cy - 11, cx + 13, cy + 15, a.light, outline=False)
        _eyes(pen, a, cy - 3, spread=6)
    else:
        _eyes(pen, a, cy - 3)
    if "fox_cheeks" in a.face:
        pen.poly([(cx - r + 1, cy + 2), (cx, cy + r), (cx + r - 1, cy + 2), (cx, cy + 7)], a.light, outline=False)
    if "muzzle" in a.face:
        pen.oval(cx - 7, cy + 2, cx + 7, cy + 12, a.light, outline=False)
        pen.oval(cx - 2.6, cy + 2.5, cx + 2.6, cy + 6, "#3b2a20", outline=False)
        pen.arc(cx - 4, cy + 4, cx, cy + 10, 200, 140, width=1.1)
        pen.arc(cx, cy + 4, cx + 4, cy + 10, 200, 140, width=1.1)
    if "monkey_face" in a.face:
        pen.oval(cx - 2.5, cy + 4, cx + 2.5, cy + 7, "#3b2a20", outline=False)
        pen.arc(cx - 6, cy + 4, cx + 6, cy + 12, 200, 140, width=1.2)
    if "koala_nose" in a.face:
        pen.oval(cx - 4, cy - 1, cx + 4, cy + 10, "#3a3f47", outline=False)
        pen.arc(cx - 5, cy + 6, cx + 5, cy + 15, 220, 100, width=1.1)
    if "whiskers" in a.face:
        for side in (-1, 1):
            for dy in (-1.5, 2):
                pen.line([(cx + side * 8, cy + 6 + dy / 2), (cx + side * 20, cy + 4 + dy * 1.6)], width=0.7)
    if "beak" in a.face:
        beak = a.dark if a.fur != a.dark and "crest" in a.face else "#f5a524"
        pen.poly([(cx - 5, cy + 3), (cx + 5, cy + 3), (cx, cy + 11)], beak)
    if "crest" in a.face:
        for i, dx in enumerate((-4, 0, 4)):
            pen.oval(cx + dx - 2.5, cy - r - 8 + abs(dx) * 0.6, cx + dx + 2.5, cy - r + 3, a.dark if i == 1 else a.fur)
    if "trunk" in a.face:
        pen.poly([(cx - 5, cy + 2), (cx + 5, cy + 2), (cx + 6, cy + 16), (cx + 14, cy + 22), (cx + 12, cy + 27),
                  (cx + 1, cy + 20)], a.fur, smooth=True)
    if not {"patches", "mask", "frog"} & set(a.face):
        for side in (-1, 1):  # pirospozsgás arc
            pen.circle(cx + side * 12, cy + 5, 3, cheek, outline=False)


def _body(pen: Pen, a: Animal):
    x0, y0, x1, y1 = BODY
    if "tentacles" in a.face:
        for i in range(5):
            bx = x0 + 3 + i * 7.5
            pen.poly([(bx, y0 + 2), (bx + 7, y0 + 2), (bx + 8 + (i - 2) * 2, y1 - 4), (bx + 2 + (i - 2) * 3, y1)],
                     a.fur, smooth=True)
        pen.oval(x0 + 2, y0 - 6, x1 - 2, y0 + 16, a.fur)
        return
    pen.oval(x0, y0, x1, y1, a.fur)
    if "belly" in a.face or a.ears in ("round", "pointy", "floppy", "side", "big_round", "long"):
        pen.oval(x0 + 8, y0 + 10, x1 - 8, y1 - 4, a.light, outline=False)


def _paws(pen: Pen, a: Animal, paws: List[Tuple[float, float]]):
    color = a.dark if a.ears in ("round", "big_round") and "patches" in a.face else a.fur
    for px, py in paws:
        pen.circle(px, py, 4.2, color)


# --- hangszerek: a rajz után a mancsok helye ---------------------------------------------

def _piano(pen, ink):
    pen.rect(46, 60, 98, 96, ink["wood"])
    pen.rect(49, 63, 95, 74, ink["dark"])
    pen.rect(49, 74, 95, 82, "#fbfbfb")
    for i in range(1, 9):
        pen.line([(49 + i * 5.1, 74), (49 + i * 5.1, 82)], width=0.6)
    for i in (1, 2, 4, 5, 6, 8):
        pen.rect(48 + i * 5.1, 74, 50.6 + i * 5.1, 78.5, "#222222", outline=False)
    pen.line([(70, 63), (70, 58)], fill=ink["metal"], width=1)
    return [(54, 76), (66, 75)]


def _xylophone(pen, ink):
    colors = [ink["accent"], ink["metal"], ink["accent2"], ink["wood"], ink["accent"]]
    for i, col in enumerate(colors):
        x = 52 + i * 8.5
        pen.rect(x, 68 - i * 1.5, x + 6.5, 90 + i * 1.5, col)
    pen.line([(48, 80), (96, 76)], width=1.2)
    pen.line([(60, 58), (68, 70)], fill=ink["dark"], width=1.6)
    pen.circle(68.5, 71, 2.3, ink["accent2"])
    return [(59, 58), (40, 72)]


def _organ_pipes(pen, ink):
    for i, h in enumerate((30, 40, 52, 44, 34)):
        x = 58 + i * 8
        pen.rect(x, 92 - h - 30, x + 6, 70, ink["metal"])
        pen.oval(x + 1.2, 92 - h - 26, x + 4.8, 92 - h - 23, ink["dark"], outline=False)


def _organ(pen, ink):
    pen.rect(48, 68, 98, 78, ink["wood"])
    pen.rect(50, 78, 96, 85, "#fbfbfb")
    for i in range(1, 9):
        pen.line([(50 + i * 5.1, 78), (50 + i * 5.1, 85)], width=0.6)
    return [(56, 80), (70, 80)]


def _guitar(pen, ink, scale=1.0, color=None):
    body = color or ink["wood"]
    neck_end = (88, 44 - (scale - 1) * 20)
    pen.line([(54, 76), neck_end], fill=ink["dark"], width=4.5 * scale)
    pen.line([neck_end, (neck_end[0] + 4, neck_end[1] - 4)], fill=ink["dark"], width=5.5 * scale)
    pen.circle(50, 80, 9 * scale, body)
    pen.circle(58, 72, 7 * scale, body)
    pen.circle(53, 77, 2.8 * scale, ink["dark"], outline=False)
    for off in (-0.8, 0.8):
        pen.line([(48, 82 + off), neck_end], fill=ink["metal"], width=0.5)
    return [(47, 70), (76, 54 - (scale - 1) * 10)]


def _bass(pen, ink):
    return _guitar(pen, ink, scale=1.25, color=ink["accent"])


def _violin(pen, ink):
    pen.oval(46, 52, 62, 70, ink["wood"])
    pen.oval(48, 57, 60, 66, mix(ink["wood"], "#000000", 0.25), outline=False)
    pen.line([(54, 54), (73, 40)], fill=ink["dark"], width=2.2)
    pen.line([(36, 72), (86, 50)], fill=ink["metal"], width=1.2)
    return [(70, 42), (40, 70)]


def _choir(pen, ink):
    pen.rect(46, 62, 74, 84, "#fbfbfb")
    pen.line([(60, 62), (60, 84)], width=0.8)
    for y in (67, 71, 75, 79):
        pen.line([(49, y), (57, y)], fill=ink["dark"], width=0.5)
        pen.line([(63, y), (71, y)], fill=ink["dark"], width=0.5)
    _note(pen, ink["accent"], 74, 34)
    _note(pen, ink["accent2"], 84, 22)
    return [(47, 72), (73, 72)]


def _note(pen, color, x, y):
    pen.oval(x - 3.5, y + 6, x + 1.5, y + 10, color)
    pen.line([(x + 1.3, y + 8), (x + 1.3, y - 4), (x + 6, y - 1)], fill=color, width=1.4)


def _trumpet(pen, ink):
    # az elefánt az ormányával fúj bele
    pen.line([(58, 61), (80, 61)], fill=ink["metal"], width=3.4)
    pen.poly([(78, 61), (94, 52), (94, 70)], ink["metal"])
    for x in (64, 69, 74):
        pen.rect(x - 1.2, 54, x + 1.2, 61, ink["metal"], width=0.8)
    pen.line([(62, 63), (76, 65)], fill=ink["metal"], width=2)
    return [(64, 68), (73, 67)]


def _sax(pen, ink):
    pen.line([(46, 47), (54, 52), (58, 60)], fill=ink["metal"], width=2.2)
    pen.poly([(56, 58), (62, 58), (66, 86), (72, 90), (78, 76), (84, 76), (78, 96), (60, 92)], ink["metal"], smooth=True)
    pen.oval(76, 72, 88, 80, mix(ink["metal"], "#000000", 0.25))
    for y in (66, 72, 78):
        pen.circle(63 + (y - 66) * 0.18, y, 1.4, ink["dark"], outline=False)
    return [(61, 64), (66, 82)]


def _flute(pen, ink):
    pen.rect(44, 46.5, 96, 50.5, ink["metal"])
    for x in (60, 66, 72, 78, 84):
        pen.circle(x, 48.5, 0.9, ink["dark"], outline=False)
    _note(pen, ink["accent"], 86, 26)
    return [(66, 51), (80, 51)]


def _keytar(pen, ink):
    pen.poly([(42, 82), (92, 62), (96, 72), (46, 92)], ink["accent"])
    pen.poly([(48, 81), (84, 66.5), (86.5, 71), (50.5, 86)], "#fbfbfb", width=0.8)
    for i in range(1, 8):
        x = 48 + i * 4.5
        pen.line([(x, 81 - i * 1.8), (x + 2.5, 86 - i * 1.85)], width=0.5)
    pen.line([(92, 62), (98, 58)], fill=ink["dark"], width=3)
    return [(54, 82), (88, 66)]


def _pad(pen, ink):
    cx, cy, r = HEAD
    pen.arc(cx - r - 2, cy - r - 4, cx + r + 2, cy + r, 20, 140, fill=ink["dark"], width=2.4)
    for side in (-1, 1):
        pen.rect(cx + side * (r + 1) - 3.5, cy - 4, cx + side * (r + 1) + 3.5, cy + 7, ink["accent2"])
    pen.rect(44, 70, 96, 90, ink["dark"])
    for i in range(4):
        for j in range(2):
            pen.rect(48 + i * 11.5, 73 + j * 8.5, 56 + i * 11.5, 79.5 + j * 8.5,
                     ink["accent"] if (i + j) % 2 else ink["accent2"], width=0.7)
    return [(52, 76), (74, 84)]


def _knobs(pen, ink):
    pen.rect(46, 66, 98, 92, ink["dark"])
    for i in range(3):
        x = 55 + i * 15
        pen.circle(x, 74, 4.2, ink["metal"])
        a = math.radians(210 - i * 70)
        pen.line([(x, 74), (x + 3.5 * math.cos(a), 74 - 3.5 * math.sin(a))], fill=ink["dark"], width=1)
    pts = [(50 + i * 2, 86 - 3.5 * math.sin(i * 0.9)) for i in range(23)]
    pen.line(pts, fill=ink["accent2"], width=1.2, smooth=True)
    return [(48, 72), (96, 80), (60, 92)]


def _banjo(pen, ink):
    pen.line([(56, 76), (92, 40)], fill=ink["wood"], width=3.6)
    pen.rect(89, 36, 95, 42, ink["dark"])
    pen.circle(54, 78, 11, ink["metal"])
    pen.circle(54, 78, 8.5, "#f8f4e6")
    for off in (-0.7, 0.7):
        pen.line([(50, 82 + off), (91, 41 + off)], fill=ink["dark"], width=0.4)
    return [(52, 70), (80, 52)]


def _drum(pen, ink):
    pen.rect(50, 74, 90, 94, ink["accent"])
    for i in range(5):
        x = 50 + i * 10
        pen.line([(x, 74), (x + 10, 94)], fill=ink["metal"], width=0.7)
    pen.oval(50, 69, 90, 79, "#f8f4e6")
    pen.line([(56, 58), (66, 72)], fill=ink["wood"], width=1.8)
    pen.line([(84, 56), (76, 72)], fill=ink["wood"], width=1.8)
    return [(55, 57), (85, 55)]


def _megaphone(pen, ink):
    pen.poly([(56, 56), (82, 44), (82, 72), (56, 62)], ink["accent"])
    pen.oval(79, 44, 85, 72, mix(ink["accent"], "#ffffff", 0.3))
    for i, r in enumerate((6, 11, 16)):
        pen.arc(84 - r, 58 - r, 84 + r, 58 + r, -40, 80, fill=ink["accent2"], width=1.3 - i * 0.2)
    return [(57, 61), (66, 66)]


INSTRUMENTS = {
    "piano": _piano, "xylophone": _xylophone, "organ": _organ, "guitar": _guitar, "bass": _bass,
    "violin": _violin, "choir": _choir, "trumpet": _trumpet, "sax": _sax, "flute": _flute, "keytar": _keytar,
    "pad": _pad, "knobs": _knobs, "banjo": _banjo, "drum": _drum, "megaphone": _megaphone,
}
BACKDROPS = {"organ": _organ_pipes}   # az állat mögé kerülő rész


def inks(palette: dict) -> dict:
    """A hangszerek színei a skinből: így a rajz illik a választott megjelenéshez."""
    return {
        "accent": palette["accent"],
        "accent2": palette["accent2"],
        "metal": palette["sun_top"],
        "wood": mix(palette["sun_bottom"], "#7a4a24", 0.55),
        "dark": "#2a2530",
    }


def paint(canvas, program: int, x: float, y: float, size: float, palette: dict, tag: str = "art") -> Family:
    """Az állat a hangszerével a (x, y) bal felső sarkú, size × size dobozban."""
    family = family_of(program)
    animal = ANIMALS[family.animal]
    ink = inks(palette)
    pen = Pen(canvas, x, y, size, outline=mix(palette["fg"], palette["bg"], 0.25), tag=tag)
    pen.oval(4, 4, 96, 104, mix(palette["bg"], palette["accent"], 0.14), outline=False)  # reflektorfény
    pen.oval(14, 92, 92, 102, mix(palette["bg"], "#000000", 0.25), outline=False)        # árnyék
    draw = INSTRUMENTS[family.instrument]
    cheek = mix(palette["accent"], "#ff8fa3", 0.5)
    if family.instrument in BACKDROPS:
        BACKDROPS[family.instrument](pen, ink)
    _body(pen, animal)
    _head(pen, animal, cheek)
    paws = draw(pen, ink)
    _paws(pen, animal, paws)
    return family
