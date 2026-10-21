"""Színsegédek és paletta építő.

Egy skin variáns néhány alapszínből áll (háttér, felület, szöveg, két akcentus,
naplemente színátmenet, rács). A `make_palette` ebből előállítja a felület összes
színtokenjét, és a szöveg / gomb párokat addig igazítja, amíg el nem érik a
WCAG 4.5 : 1 kontrasztot — így minden skin olvasható marad.
"""

from typing import Iterable, Optional, Sequence

MIN_CONTRAST = 4.5

# a felület által használt tokenek (minden palettában mind megvan)
TOKENS = (
    "bg", "surface", "fg", "muted", "border", "accent", "accent_fg", "select_bg", "piano_bg",
    "key_white", "key_black", "key_white_active", "key_black_active", "key_outline", "key_label",
    "log_bg", "log_fg", "accent2", "section_fg", "header_bg", "title_fg",
    "sun_top", "sun_mid", "sun_bottom", "grid",
)

# a kontraszt ellenőrzés párjai: (előtér, háttér)
TEXT_PAIRS = (
    ("fg", "bg"), ("fg", "surface"), ("muted", "bg"), ("muted", "surface"), ("accent_fg", "accent"),
    ("log_fg", "log_bg"), ("section_fg", "bg"), ("title_fg", "header_bg"), ("fg", "select_bg"),
    ("key_label", "key_white"),
)


def _rgb(color: str):
    return [int(color[i:i + 2], 16) for i in (1, 3, 5)]


def luminance(color: str) -> float:
    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = _rgb(color)
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(fg: str, bg: str) -> float:
    """WCAG kontrasztarány két #rrggbb szín között (1 … 21)."""
    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """Két #rrggbb szín keveréke (t = 0 → a, t = 1 → b)."""
    t = min(max(t, 0.0), 1.0)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(_rgb(a), _rgb(b)))


def is_dark(color: str) -> bool:
    return luminance(color) < 0.18


def ensure_contrast(color: str, backgrounds: Iterable[str], ratio: float = MIN_CONTRAST) -> str:
    """A színt a háttértől elfelé (világos háttéren sötétebbre, sötéten világosabbra) tolja, amíg mindegyik
    háttérrel eléri a kívánt kontrasztot."""
    backgrounds = list(backgrounds)
    target = "#000000" if not is_dark(backgrounds[0]) else "#ffffff"
    for step in range(21):
        candidate = mix(color, target, step / 20)
        if all(contrast(candidate, bg) >= ratio for bg in backgrounds):
            return candidate
    return target


def best_text_on(color: str, dark: str = "#101018", light: str = "#ffffff") -> str:
    """Olvasható szöveg szín egy kitöltött háttéren (gomb)."""
    return dark if contrast(dark, color) >= contrast(light, color) else light


def make_palette(
    bg: str,
    surface: str,
    fg: str,
    accent: str,
    accent2: str,
    sun: Sequence[str],
    grid: str,
    piano_bg: Optional[str] = None,
    key_white: Optional[str] = None,
    key_black: Optional[str] = None,
    header_bg: Optional[str] = None,
) -> dict:
    dark = is_dark(bg)
    fg = ensure_contrast(fg, (bg, surface), 7.0)
    header_bg = header_bg or bg
    select_bg = mix(surface, accent2, 0.35 if dark else 0.25)
    if contrast(fg, select_bg) < MIN_CONTRAST:
        select_bg = mix(surface, accent2, 0.18)
    key_white = key_white or mix("#ffffff", accent2, 0.05 if dark else 0.03)
    key_black = key_black or mix("#14141c", accent, 0.12)
    log_bg = mix(bg, "#000000", 0.3) if dark else mix(bg, "#ffffff", 0.65)
    accent_fg = best_text_on(accent)
    if contrast(accent_fg, accent) < MIN_CONTRAST:  # középtónusú akcentus: a gomb háttere igazodik
        accent = ensure_contrast(accent, (accent_fg,), MIN_CONTRAST)
    palette = {
        "bg": bg,
        "surface": surface,
        "fg": fg,
        "muted": ensure_contrast(mix(fg, bg, 0.35), (bg, surface)),
        "border": mix(bg, fg, 0.25),
        "accent": accent,
        "accent_fg": accent_fg,
        "select_bg": select_bg,
        "piano_bg": piano_bg or (mix(bg, "#000000", 0.25) if dark else mix(bg, fg, 0.08)),
        "key_white": key_white,
        "key_black": key_black,
        "key_white_active": accent2,
        "key_black_active": accent,
        "key_outline": mix(key_black, bg, 0.35),
        "key_label": ensure_contrast(mix(key_black, accent, 0.35), (key_white,)),
        "log_bg": log_bg,
        "log_fg": ensure_contrast(fg, (log_bg,)),
        "accent2": accent2,
        "section_fg": ensure_contrast(accent2 if dark else accent, (bg,)),
        "header_bg": header_bg,
        "title_fg": ensure_contrast(fg, (header_bg,)),
        "sun_top": sun[0],
        "sun_mid": sun[1],
        "sun_bottom": sun[2],
        "grid": grid,
    }
    return palette


def check(palette: dict) -> list:
    """A kontraszt követelményt nem teljesítő párok (üres lista = rendben)."""
    return [
        (fg, bg, round(contrast(palette[fg], palette[bg]), 2))
        for fg, bg in TEXT_PAIRS
        if contrast(palette[fg], palette[bg]) < MIN_CONTRAST
    ]
