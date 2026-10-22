"""Skin nyilvántartás (Registry minta).

Egy `Skin` egy névvel ellátott megjelenés sötét és világos változattal: paletták,
betűtípus preferencia, a widgetek stílus tokenjei és a fejléc rajzoló (Strategy).
A felület a nyilvántartásból listáz, így új skin felvétele egyetlen `register` hívás.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from synth_mido.core.i18n import t

DARK = "dark"
LIGHT = "light"
SYSTEM = "system"
VARIANTS = (DARK, LIGHT, SYSTEM)
VARIANTS_ORDER = (DARK, LIGHT, SYSTEM)  # a választó sorrendje


def variant_label(variant: str) -> str:
    """A változat felirata az aktuális nyelven (Sötét / Világos / Rendszer)."""
    return t(f"variant.{variant}")

DEFAULT_SKIN = "synthwave"
DEFAULT_VARIANT = DARK


@dataclass(frozen=True)
class WidgetStyle:
    """A gombok és egyéb widgetek alakja, a színeken túl (TASK-013.03)."""

    title_upper: bool = False                 # szakaszcímek nagybetűvel
    button_padding: Tuple[int, int] = (12, 5)
    border_width: int = 1
    relief: str = "flat"                      # flat / solid / raised / ridge / groove
    frame_relief: str = "solid"
    button_edge: str = "border"               # a gomb keretének színtokenje (pl. "accent2" neon kerethez)
    bold_buttons: bool = False                # az elsődleges gomb mindig félkövér


@dataclass(frozen=True)
class Skin:
    id: str
    name: str
    dark: dict
    light: dict
    fonts: Sequence[str] = ("Segoe UI", "DejaVu Sans")
    style: WidgetStyle = field(default_factory=WidgetStyle)
    painter: Optional[Callable] = None       # fejléc rajzoló: painter(canvas, width, height, palette, font, dark)
    header_height: int = 92
    effect: str = "flames"                  # a hozzá illő hangeffekt (fx.effects azonosító)

    def palette(self, scheme: str) -> dict:
        return self.light if scheme == LIGHT else self.dark

    @property
    def label(self) -> str:
        """A skin neve az aktuális nyelven (a `name` a magyar alapnév)."""
        return t(f"skin.{self.id}") if t(f"skin.{self.id}") != f"skin.{self.id}" else self.name


_SKINS: Dict[str, Skin] = {}


def register(skin: Skin) -> Skin:
    if skin.id in _SKINS:
        raise ValueError(f"A(z) {skin.id!r} skin már létezik")
    _SKINS[skin.id] = skin
    return skin


def get(skin_id: str) -> Skin:
    """A skin, vagy ismeretlen azonosítónál az alapértelmezett."""
    return _SKINS.get(skin_id) or _SKINS[DEFAULT_SKIN]


def all_skins() -> List[Skin]:
    return list(_SKINS.values())


def by_name(name: str) -> Optional[Skin]:
    return next((s for s in _SKINS.values() if name in (s.name, s.label)), None)


def choose_font(fonts: Sequence[str], available) -> str:
    available = set(available)
    return next((f for f in fonts if f in available), "Segoe UI")
