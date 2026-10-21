"""Fejléc jelenetek (Strategy minta): skinenként egy rajzoló függvény.

Minden rajzoló ugyanazt kapja: `painter(canvas, width, height, palette, font, dark)`.
Csak Tk vászon primitíveket használ (nincs képfájl), és a szélességhez igazodik.
A cím a bal oldalra kerül, a jelenet fő elemei jobbra, hogy ne takarják egymást.
"""

import math
import random

from synth_mido.core import i18n
from synth_mido.core.i18n import t
from synth_mido.skins.palette import mix

TITLE = "SYNTH-MIDO"


# --- közös segédek ---------------------------------------------------------------

def gradient(c, x0, y0, x1, y1, top, bottom, bands=16):
    for i in range(bands):
        ya = y0 + (y1 - y0) * i / bands
        yb = y0 + (y1 - y0) * (i + 1) / bands + 1
        c.create_rectangle(x0, ya, x1, yb, outline="", fill=mix(top, bottom, i / max(bands - 1, 1)))


def stars(c, width, bottom, color, count, seed=3, size=1.6):
    rng = random.Random(seed)
    for _ in range(count):
        x, y = rng.uniform(0, width), rng.uniform(0, bottom)
        r = rng.uniform(0.5, size)
        c.create_oval(x - r, y - r, x + r, y + r, outline="", fill=color)


def title(c, p, font, height, upper=True, shadow=True, size=24, color=None, sub_color=None):
    text = " ".join(TITLE) if upper else "Synth-Mido"
    y = height * 0.36
    if shadow:
        c.create_text(26, y + 2, anchor="w", text=text, fill=p["accent"], font=(font, size, "bold"))
    c.create_text(24, y, anchor="w", text=text, fill=color or (p["accent2"] if shadow else p["title_fg"]),
                  font=(font, size, "bold"))
    c.create_text(26, y + size * 0.95, anchor="w", text=i18n.upper(t("header.subtitle")).replace(" · ", "  ·  ") if upper else t("header.subtitle"),
                  fill=sub_color or p["title_fg"], font=(font, 9, "bold"))


def polygon(c, points, **kw):
    c.create_polygon(*[v for pt in points for v in pt], **kw)


# --- skinek -------------------------------------------------------------------------

def paint_synthwave(c, w, h, p, font, dark):
    horizon = int(h * 0.64)
    gradient(c, 0, 0, w, horizon, p["header_bg"], "#4a1260" if dark else "#ffc4e1", 14)
    r = h * 0.52
    cx, cy = w - 150, horizon - r * 0.15
    top = int(cy - r)
    for y in range(max(top, 0), horizon):
        dy = y - cy
        if abs(dy) >= r:
            continue
        t = (y - top) / max(horizon - top, 1)
        if t > 0.45 and (y - top) % 7 < 1 + int((t - 0.45) * 8):
            continue
        half = (r * r - dy * dy) ** 0.5
        color = mix(p["sun_top"], p["sun_mid"], t / 0.5) if t < 0.5 else mix(p["sun_mid"], p["sun_bottom"], (t - 0.5) / 0.5)
        c.create_line(cx - half, y, cx + half, y, fill=color)
    c.create_rectangle(0, horizon, w, h, outline="", fill=mix(p["header_bg"], "#12032b" if dark else "#f6d6ff", 0.5))
    vx = w / 2
    for i in range(-14, 15):
        c.create_line(vx + i * w / 70, horizon, vx + i * w / 6, h, fill=mix(p["header_bg"], p["grid"], 0.55))
    for k in range(1, 7):
        y = horizon + (h - horizon) * (k / 6) ** 2
        c.create_line(0, y, w, y, fill=mix(p["header_bg"], p["grid"], 0.25 + 0.6 * k / 6))
    c.create_line(0, horizon, w, horizon, fill=p["accent"], width=2)
    title(c, p, font, horizon / 0.72 * 0.8, sub_color=p["sun_top"] if dark else p["accent"])


def paint_classic(c, w, h, p, font, dark):
    c.create_text(12, h / 2, anchor="w", text="SYNTH-MIDO", fill=p["title_fg"], font=(font, 13, "bold"))
    c.create_text(140, h / 2, anchor="w", text=t("app.title"), fill=p["muted"], font=(font, 9))
    c.create_line(0, h - 1, w, h - 1, fill=p["border"])


def paint_astronaut(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h, p["header_bg"], mix(p["header_bg"], p["accent2"], 0.25), 12)
    stars(c, w, h, mix(p["title_fg"], p["header_bg"], 0.2), int(w / 9))
    # gyűrűs bolygó
    px, py, pr = w - 120, h * 0.55, h * 0.32
    c.create_oval(px - pr * 1.9, py - pr * 0.45, px + pr * 1.9, py + pr * 0.45, outline=p["sun_mid"], width=3)
    c.create_oval(px - pr, py - pr, px + pr, py + pr, outline="", fill=p["accent"])
    c.create_oval(px - pr * 0.6, py - pr * 0.75, px + pr * 0.1, py - pr * 0.35, outline="", fill=mix(p["accent"], "#ffffff", 0.3))
    c.create_arc(px - pr * 1.9, py - pr * 0.45, px + pr * 1.9, py + pr * 0.45, start=180, extent=180,
                 style="arc", outline=p["sun_mid"], width=3)
    # űrhajós sisak
    ax, ay, ar = w - 290, h * 0.5, h * 0.26
    c.create_oval(ax - ar, ay - ar, ax + ar, ay + ar, outline=p["accent2"], width=2, fill=mix(p["header_bg"], "#ffffff", 0.85))
    c.create_oval(ax - ar * 0.7, ay - ar * 0.5, ax + ar * 0.7, ay + ar * 0.45, outline="", fill=p["header_bg"])
    c.create_arc(ax - ar * 0.55, ay - ar * 0.4, ax + ar * 0.2, ay + ar * 0.2, start=100, extent=70, style="arc",
                 outline=p["accent2"], width=2)
    # hold sarló
    c.create_oval(w * 0.55, 10, w * 0.55 + 26, 36, outline="", fill=p["sun_top"])
    c.create_oval(w * 0.55 + 8, 8, w * 0.55 + 34, 34, outline="", fill=mix(p["header_bg"], p["accent2"], 0.08))
    title(c, p, font, h)


def paint_safari(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h * 0.75, p["sun_top"] if not dark else p["header_bg"], p["sun_bottom"], 14)
    c.create_oval(w - 210, h * 0.2, w - 110, h * 1.1, outline="", fill=p["sun_top"])
    ground = mix(p["header_bg"], "#000000", 0.5) if dark else mix(p["fg"], p["sun_bottom"], 0.3)
    c.create_rectangle(0, h * 0.75, w, h, outline="", fill=ground)
    # akácfa
    tx = w - 330
    c.create_line(tx, h * 0.78, tx + 6, h * 0.45, fill=ground, width=5)
    for dx, dy, rw in ((-30, 0.42, 46), (10, 0.36, 52), (40, 0.44, 40)):
        c.create_oval(tx + dx - rw, h * dy - 8, tx + dx + rw, h * dy + 8, outline="", fill=ground)
    # zsiráf
    gx, gy = w - 160, h * 0.78
    polygon(c, [(gx - 26, gy - 30), (gx + 14, gy - 32), (gx + 18, gy - 20), (gx - 24, gy - 18)], fill=ground)
    for lx in (-22, -12, 6, 14):
        c.create_line(gx + lx, gy - 20, gx + lx, gy, fill=ground, width=3)
    c.create_line(gx + 12, gy - 30, gx + 26, gy - 66, fill=ground, width=6)
    polygon(c, [(gx + 22, gy - 70), (gx + 40, gy - 66), (gx + 26, gy - 60)], fill=ground)
    for bx in (w * 0.5, w * 0.53, w * 0.58):  # madarak
        c.create_line(bx - 6, 18, bx, 22, bx + 6, 18, fill=ground, width=2)
    title(c, p, font, h, upper=False, shadow=False, color=p["title_fg"])


def paint_cartography(c, w, h, p, font, dark):
    c.create_rectangle(0, 0, w, h, outline="", fill=p["header_bg"])
    line = mix(p["header_bg"], p["grid"], 0.8)
    for i in range(0, int(w), 60):  # hosszúsági körök (enyhén ívelt)
        c.create_arc(i - 30, -h, i + 30, 2 * h, start=90, extent=180, style="arc", outline=line)
    for y in range(12, int(h), 22):
        c.create_line(0, y, w, y, fill=line, dash=(2, 4))
    rng = random.Random(9)
    for k in range(5):  # szintvonalak
        cx, cy = w * 0.62, h * 0.55
        rx, ry = 30 + k * 26, 12 + k * 9
        pts = []
        for a in range(0, 360, 20):
            j = 1 + rng.uniform(-0.12, 0.12)
            pts.append((cx + rx * j * math.cos(math.radians(a)), cy + ry * j * math.sin(math.radians(a))))
        polygon(c, pts, outline=mix(p["header_bg"], p["accent2"], 0.4 + k * 0.1), fill="", smooth=True)
    # útvonal és X
    c.create_line(w * 0.35, h * 0.8, w * 0.45, h * 0.3, w * 0.55, h * 0.7, w * 0.7, h * 0.4, fill=p["accent"],
                  width=2, dash=(6, 4), smooth=True)
    c.create_text(w * 0.7, h * 0.4, text="✕", fill=p["accent"], font=(font, 16, "bold"))
    # szélrózsa
    rx, ry, r = w - 70, h / 2, h * 0.38
    for a in range(0, 360, 45):
        rr = r if a % 90 == 0 else r * 0.55
        x2, y2 = rx + rr * math.sin(math.radians(a)), ry - rr * math.cos(math.radians(a))
        xl, yl = rx + r * 0.16 * math.sin(math.radians(a - 90)), ry - r * 0.16 * math.cos(math.radians(a - 90))
        polygon(c, [(rx, ry), (xl, yl), (x2, y2)], fill=p["accent"] if a % 90 == 0 else p["accent2"], outline="")
    c.create_text(rx, ry - r - 7, text="N", fill=p["title_fg"], font=(font, 9, "bold"))
    title(c, p, font, h, upper=False, shadow=False)


def paint_mathematics(c, w, h, p, font, dark):
    c.create_rectangle(0, 0, w, h, outline="", fill=p["header_bg"])
    grid = mix(p["header_bg"], p["grid"], 0.6)
    for x in range(0, int(w), 14):
        c.create_line(x, 0, x, h, fill=grid)
    for y in range(0, int(h), 14):
        c.create_line(0, y, w, y, fill=grid)
    ox, oy = w * 0.42, h * 0.55
    c.create_line(ox - 10, oy, w - 20, oy, fill=p["muted"], arrow="last")
    c.create_line(ox, h - 4, ox, 6, fill=p["muted"], arrow="last")
    sine = [(x, oy - math.sin((x - ox) / 22) * h * 0.3) for x in range(int(ox), int(w - 20), 4)]
    c.create_line(*[v for pt in sine for v in pt], fill=p["accent2"], width=2, smooth=True)
    para = [(x, oy - ((x - ox - (w - ox) * 0.45) / 40) ** 2 * 6 + h * 0.3) for x in range(int(ox), int(w - 20), 4)]
    para = [(x, y) for x, y in para if 4 < y < h - 4]
    if len(para) > 1:
        c.create_line(*[v for pt in para for v in pt], fill=p["accent"], width=2, smooth=True)
    for text, x, y, size in (("e^(iπ) + 1 = 0", w * 0.66, h * 0.2, 11), ("∫ f(x) dx", w * 0.82, h * 0.78, 11),
                             ("π", w - 40, h * 0.25, 20), ("Σ", w * 0.5, h * 0.82, 16), ("√2", w * 0.58, h * 0.25, 12)):
        c.create_text(x, y, text=text, fill=p["title_fg"], font=(font, size, "italic"))
    title(c, p, font, h, upper=False, shadow=False)


def paint_antiquity(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h, p["header_bg"], mix(p["header_bg"], p["sun_mid"], 0.35), 10)
    stone = mix(p["header_bg"], p["fg"], 0.55)
    tx, base, tw = w - 260, h - 10, 200
    polygon(c, [(tx, base - 56), (tx + tw / 2, base - 76), (tx + tw, base - 56)], fill=stone, outline="")
    c.create_rectangle(tx - 4, base - 58, tx + tw + 4, base - 50, fill=stone, outline="")
    for i in range(6):
        x = tx + 10 + i * (tw - 20) / 5
        c.create_rectangle(x - 6, base - 50, x + 6, base - 6, fill=stone, outline="")
        for k in (-3, 0, 3):
            c.create_line(x + k, base - 48, x + k, base - 8, fill=mix(stone, p["header_bg"], 0.35))
    c.create_rectangle(tx - 10, base - 6, tx + tw + 10, base, fill=stone, outline="")
    # görög meander a fejléc alján
    y, s = h - 4, 8
    x = 0
    pts = []
    while x < w * 0.45:
        pts += [(x, y), (x, y - s), (x + s * 1.5, y - s), (x + s * 1.5, y - s / 2), (x + s * 0.75, y - s / 2),
                (x + s * 0.75, y), (x + s * 2, y)]
        x += s * 2
    c.create_line(*[v for pt in pts for v in pt], fill=p["accent"], width=2)
    # babérág
    for i in range(7):
        lx = w * 0.55 + i * 14
        c.create_oval(lx, h * 0.3 - (i % 2) * 8, lx + 12, h * 0.3 + 6 - (i % 2) * 8, fill=p["accent2"], outline="")
    title(c, p, font, h, upper=False, shadow=False)


def paint_ocean(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h * 0.45, p["header_bg"], mix(p["header_bg"], p["sun_top"], 0.35), 8)
    c.create_oval(w - 180, h * 0.12, w - 130, h * 0.12 + 50, outline="", fill=p["sun_top"])
    for k in range(4):
        y0 = h * (0.45 + k * 0.14)
        col = mix(p["header_bg"], p["accent2"], 0.35 + k * 0.17)
        pts = [(0, h)] + [(x, y0 + math.sin(x / 38 + k) * 5) for x in range(0, int(w) + 10, 10)] + [(w, h)]
        polygon(c, pts, fill=col, outline="", smooth=True)
    for fx, fy in ((w * 0.6, h * 0.75), (w * 0.72, h * 0.88), (w - 70, h * 0.7)):
        polygon(c, [(fx, fy), (fx + 18, fy - 6), (fx + 26, fy), (fx + 18, fy + 6)], fill=p["accent"], outline="")
        polygon(c, [(fx, fy), (fx - 8, fy - 6), (fx - 8, fy + 6)], fill=p["accent"], outline="")
    rng = random.Random(5)
    for _ in range(12):
        bx, by, br = rng.uniform(w * 0.5, w), rng.uniform(h * 0.5, h), rng.uniform(1.5, 4)
        c.create_oval(bx - br, by - br, bx + br, by + br, outline=mix(p["accent2"], "#ffffff", 0.5))
    title(c, p, font, h * 0.85, upper=False, shadow=False)


def paint_forest(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h, p["header_bg"], mix(p["header_bg"], p["sun_mid"], 0.25), 10)
    c.create_oval(w - 160, 10, w - 120, 50, outline="", fill=p["sun_top"])
    rng = random.Random(11)
    for row, (shade, base, size) in enumerate(((0.35, h * 0.85, 0.55), (0.6, h * 0.95, 0.75), (0.85, h + 6, 0.95))):
        col = mix(p["header_bg"], p["accent2"] if dark else p["fg"], shade * (0.7 if dark else 0.6))
        x = rng.uniform(-20, 10) + w * 0.38
        while x < w + 20:
            th = h * size * rng.uniform(0.7, 1.0)
            polygon(c, [(x, base - th), (x - th * 0.32, base), (x + th * 0.32, base)], fill=col, outline="")
            x += th * rng.uniform(0.35, 0.6)
    for _ in range(14):
        fx, fy = rng.uniform(w * 0.4, w), rng.uniform(h * 0.3, h * 0.9)
        c.create_oval(fx - 1.5, fy - 1.5, fx + 1.5, fy + 1.5, outline="", fill=p["sun_top"])
    title(c, p, font, h, upper=False, shadow=False)


def paint_sakura(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h, p["header_bg"], mix(p["header_bg"], p["accent"], 0.25), 10)
    c.create_oval(w - 230, 14, w - 170, 74, outline="", fill=p["sun_bottom"])
    fx, base = w - 330, h
    polygon(c, [(fx - 120, base), (fx - 22, base - h * 0.68), (fx + 22, base - h * 0.68), (fx + 120, base)],
            fill=mix(p["header_bg"], p["accent2"], 0.45), outline="")
    polygon(c, [(fx - 22, base - h * 0.68), (fx + 22, base - h * 0.68), (fx + 38, base - h * 0.5),
                (fx + 12, base - h * 0.55), (fx - 4, base - h * 0.48), (fx - 38, base - h * 0.5)], fill="#ffffff", outline="")
    branch = mix(p["fg"], p["header_bg"], 0.3)
    c.create_line(w, 8, w - 90, 30, w - 160, 26, w - 210, 44, fill=branch, width=4, smooth=True)
    c.create_line(w - 90, 30, w - 110, 56, fill=branch, width=3)
    rng = random.Random(21)
    for bx, by in ((w - 30, 14), (w - 70, 26), (w - 120, 30), (w - 150, 24), (w - 200, 42), (w - 108, 56), (w - 180, 36)):
        for a in range(0, 360, 72):
            px, py = bx + 5 * math.cos(math.radians(a)), by + 5 * math.sin(math.radians(a))
            c.create_oval(px - 4, py - 4, px + 4, py + 4, outline="", fill=p["accent"])
        c.create_oval(bx - 2, by - 2, bx + 2, by + 2, outline="", fill=p["sun_top"])
    for _ in range(10):
        px, py = rng.uniform(w * 0.45, w), rng.uniform(h * 0.4, h)
        c.create_oval(px, py, px + 6, py + 3, outline="", fill=mix(p["accent"], "#ffffff", 0.3))
    title(c, p, font, h, upper=False, shadow=False)


def gear(c, cx, cy, r, teeth, fill, hole):
    pts = []
    for i in range(teeth * 2):
        a = math.pi * i / teeth
        rr = r if i % 2 == 0 else r * 0.8
        pts += [(cx + rr * math.cos(a - 0.12), cy + rr * math.sin(a - 0.12)), (cx + rr * math.cos(a + 0.12), cy + rr * math.sin(a + 0.12))]
    polygon(c, pts, fill=fill, outline="")
    c.create_oval(cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35, fill=hole, outline="")


def paint_steampunk(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h, p["header_bg"], mix(p["header_bg"], p["accent2"], 0.25), 10)
    pipe = mix(p["accent"], p["header_bg"], 0.2)
    c.create_line(w * 0.42, h * 0.8, w - 60, h * 0.8, fill=pipe, width=8)
    c.create_line(w * 0.6, h * 0.8, w * 0.6, 0, fill=pipe, width=8)
    for x in range(int(w * 0.45), int(w - 60), 40):
        c.create_oval(x - 3, h * 0.8 - 3, x + 3, h * 0.8 + 3, fill=p["sun_top"], outline="")
    gear(c, w - 90, h * 0.45, h * 0.38, 12, p["accent"], p["header_bg"])
    gear(c, w - 165, h * 0.62, h * 0.24, 9, p["accent2"], p["header_bg"])
    gear(c, w - 215, h * 0.3, h * 0.17, 8, p["accent"], p["header_bg"])
    gx, gy, gr = w * 0.6, h * 0.42, h * 0.25  # nyomásmérő
    c.create_oval(gx - gr, gy - gr, gx + gr, gy + gr, fill=mix(p["fg"], p["header_bg"], 0.1), outline=p["accent"], width=3)
    c.create_line(gx, gy, gx + gr * 0.7, gy - gr * 0.4, fill=p["accent2"], width=2)
    title(c, p, font, h, upper=True, shadow=False, color=p["title_fg"])


def paint_arcade(c, w, h, p, font, dark):
    c.create_rectangle(0, 0, w, h, outline="", fill=p["header_bg"])
    stars(c, w, h * 0.7, p["muted"], int(w / 14), seed=2, size=1.2)
    invader = ["00100000100", "00010001000", "00111111100", "01101110110", "11111111111", "10111111101", "10100000101",
               "00011011000"]
    s = 4
    for k, (ox, col) in enumerate(((w - 330, p["accent2"]), (w - 230, p["accent"]), (w - 130, p["sun_top"]))):
        oy = 14 + (k % 2) * 10
        for r, row in enumerate(invader):
            for q, bit in enumerate(row):
                if bit == "1":
                    c.create_rectangle(ox + q * s, oy + r * s, ox + q * s + s, oy + r * s + s, fill=col, outline="")
    for x in range(int(w * 0.45), int(w), 18):
        c.create_rectangle(x, h - 14, x + 4, h - 10, fill=p["sun_top"], outline="")
    c.create_line(0, h - 4, w, h - 4, fill=p["accent2"], width=2)
    c.create_text(w * 0.47, 10, anchor="nw", text="1UP  004200   HI  090000", fill=p["title_fg"], font=(font, 9, "bold"))
    title(c, p, font, h)


def paint_artdeco(c, w, h, p, font, dark):
    c.create_rectangle(0, 0, w, h, outline="", fill=p["header_bg"])
    cx, base = w - 170, h
    for i in range(19):
        a = math.radians(180 + i * 10)
        c.create_line(cx, base, cx + math.cos(a) * h * 1.6, base + math.sin(a) * h * 1.6,
                      fill=mix(p["header_bg"], p["accent"], 0.55 if i % 2 else 0.3), width=2)
    for k, s in enumerate((70, 52, 34, 18)):  # lépcsős zikkurat
        c.create_rectangle(cx - s, base - 18 * (k + 1), cx + s, base - 18 * k, fill=p["header_bg"], outline=p["accent"], width=2)
    for y in (6, h - 6):
        c.create_line(0, y, w, y, fill=p["accent"], width=2)
        c.create_line(0, y + (4 if y < h / 2 else -4), w, y + (4 if y < h / 2 else -4), fill=p["accent2"])
    for x in range(int(w * 0.45), int(w * 0.65), 16):  # cikcakk
        c.create_line(x, h * 0.5, x + 8, h * 0.4, x + 16, h * 0.5, fill=p["accent"], width=2)
    title(c, p, font, h, upper=True, shadow=False, color=p["accent"] if dark else p["title_fg"])


def paint_desert(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h * 0.7, p["header_bg"], p["sun_mid"], 14)
    c.create_oval(w - 220, h * 0.15, w - 150, h * 0.15 + 70, outline="", fill=p["sun_top"])
    for k, (y0, shade) in enumerate(((0.62, 0.35), (0.74, 0.55), (0.86, 0.75))):
        col = mix(p["sun_bottom"], p["header_bg"] if dark else p["fg"], shade * 0.6)
        pts = [(0, h)] + [(x, h * y0 + math.sin(x / (90 + k * 30) + k * 2) * 10) for x in range(0, int(w) + 10, 12)] + [(w, h)]
        polygon(c, pts, fill=col, outline="", smooth=True)
    cact = mix(p["accent2"], "#000000", 0.45)
    kx, ky = w - 330, h * 0.85
    c.create_line(kx, ky, kx, ky - 50, fill=cact, width=10, capstyle="round")
    c.create_line(kx, ky - 22, kx - 16, ky - 22, kx - 16, ky - 40, fill=cact, width=7, capstyle="round", joinstyle="round")
    c.create_line(kx, ky - 30, kx + 14, ky - 30, kx + 14, ky - 46, fill=cact, width=7, capstyle="round", joinstyle="round")
    polygon(c, [(w - 110, h * 0.72), (w - 70, h * 0.36), (w - 30, h * 0.72)], fill=mix(p["sun_bottom"], "#000000", 0.25), outline="")
    title(c, p, font, h * 0.85, upper=False, shadow=False)


def paint_arctic(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h, p["header_bg"], mix(p["header_bg"], p["accent2"], 0.2), 10)
    stars(c, w, h * 0.6, mix(p["title_fg"], p["header_bg"], 0.3), int(w / 14), seed=8, size=1.2)
    for k, col in enumerate((p["accent"], p["accent2"], p["sun_top"])):  # sarki fény
        pts = [(x, h * (0.25 + k * 0.08) + math.sin(x / 60 + k) * 10) for x in range(int(w * 0.4), int(w) + 10, 10)]
        c.create_line(*[v for pt in pts for v in pt], fill=mix(p["header_bg"], col, 0.7), width=4, smooth=True)
        c.create_line(*[v for pt in pts for v in pt], fill=mix(p["header_bg"], col, 0.35), width=10, smooth=True)
    for mx, mh, mw in ((w - 300, 0.62, 90), (w - 180, 0.75, 120), (w - 60, 0.55, 80)):
        top = h * (1 - mh)
        polygon(c, [(mx - mw, h), (mx, top), (mx + mw, h)], fill=mix(p["header_bg"], p["fg"], 0.35 if dark else 0.25), outline="")
        polygon(c, [(mx - mw * 0.28, top + h * mh * 0.28), (mx, top), (mx + mw * 0.28, top + h * mh * 0.28),
                    (mx + mw * 0.1, top + h * mh * 0.22), (mx - mw * 0.1, top + h * mh * 0.3)], fill="#ffffff", outline="")
    title(c, p, font, h, upper=False, shadow=False)


def paint_volcano(c, w, h, p, font, dark):
    gradient(c, 0, 0, w, h, p["header_bg"], mix(p["header_bg"], p["sun_bottom"], 0.35), 12)
    vx, top = w - 200, h * 0.3
    rock = mix(p["header_bg"], "#000000", 0.55) if dark else mix(p["fg"], p["header_bg"], 0.35)
    polygon(c, [(vx - 170, h), (vx - 26, top), (vx + 26, top), (vx + 170, h)], fill=rock, outline="")
    c.create_oval(vx - 30, top - 8, vx + 30, top + 8, fill=p["sun_mid"], outline="")
    for dx, length in ((-12, 0.45), (6, 0.6), (18, 0.38)):
        c.create_line(vx + dx, top, vx + dx * 2.2, top + h * length * 0.5, vx + dx * 3.1, top + h * length,
                      fill=p["accent"], width=3, smooth=True)
    for k in range(5):  # füst
        r = 10 + k * 5
        c.create_oval(vx - 20 + k * 14 - r, top - 18 - k * 14 - r, vx - 20 + k * 14 + r, top - 18 - k * 14 + r,
                      fill=mix(p["header_bg"], p["muted"], 0.35), outline="")
    rng = random.Random(4)
    for _ in range(16):
        ex, ey = vx + rng.uniform(-60, 60), top - rng.uniform(5, h * 0.3)
        c.create_oval(ex - 1.5, ey - 1.5, ex + 1.5, ey + 1.5, fill=p["accent2"], outline="")
    title(c, p, font, h, upper=True, shadow=True, color=p["title_fg"])


def paint_jazz(c, w, h, p, font, dark):
    c.create_rectangle(0, 0, w, h, outline="", fill=p["header_bg"])
    polygon(c, [(w - 200, 0), (w - 170, 0), (w - 90, h), (w - 290, h)], fill=mix(p["header_bg"], p["sun_top"], 0.18), outline="")
    rng = random.Random(6)
    x = w * 0.42
    while x < w:  # városi sziluett
        bw, bh = rng.uniform(16, 34), rng.uniform(h * 0.2, h * 0.55)
        c.create_rectangle(x, h - bh, x + bw, h, fill=mix(p["header_bg"], p["fg"], 0.12), outline="")
        for wy in range(int(h - bh + 6), int(h - 4), 9):
            if rng.random() < 0.4:
                c.create_rectangle(x + 4, wy, x + 7, wy + 3, fill=p["sun_top"], outline="")
        x += bw + 3
    for text, nx, ny, size in (("♪", w * 0.5, h * 0.3, 18), ("♫", w * 0.6, h * 0.22, 20), ("♩", w * 0.7, h * 0.35, 16),
                               ("♬", w - 60, h * 0.25, 22)):
        c.create_text(nx, ny, text=text, fill=p["accent"], font=(font, size))
    for i in range(14):  # zongora billentyű csík
        c.create_rectangle(w * 0.42 + i * 10, h - 6, w * 0.42 + i * 10 + 9, h, fill=p["fg"] if i % 2 else p["header_bg"], outline="")
    title(c, p, font, h, upper=False, shadow=False, color=p["title_fg"])
