"""Hangeffektek nyilvántartása (Registry + Strategy).

Új effekt: egy `NoteEffect` alosztály (szerepek, színek, `voice_shapes` / `spawn` /
`particle_shapes`), majd a `register` hívás ide; a skin a `Skin.effect` mezőben nevezi
meg a hozzá illő effektet. A felület (fx_view) semmit nem tud az egyes effektekről.
"""

from typing import Dict, List, Type

from synth_mido.core.i18n import t
from synth_mido.fx.effects.base import NoteEffect, Shape  # noqa: F401 — a csomag felülete
from synth_mido.fx.effects.fire import Flames, NeonBars
from synth_mido.fx.effects.nature import Bubbles, Dust, Leaves, Petals, Snow, Stars, Steam
from synth_mido.fx.effects.retro import CompassGlyphs, MathGlyphs, MusicNotes, Pixels, RomanGlyphs

EFFECTS: Dict[str, Type[NoteEffect]] = {}
DEFAULT = "flames"


def register(cls: Type[NoteEffect]) -> Type[NoteEffect]:
    if not cls.id or cls.id in EFFECTS:
        raise ValueError(f"Hibás vagy már regisztrált effekt: {cls.id!r}")
    EFFECTS[cls.id] = cls
    return cls


for _cls in (NeonBars, Flames, Petals, Leaves, Steam, Dust, Bubbles, Snow, Stars, Pixels,
             MathGlyphs, RomanGlyphs, MusicNotes, CompassGlyphs):
    register(_cls)


def ids() -> List[str]:
    return list(EFFECTS)


def create(effect_id: str, **kwargs) -> NoteEffect:
    """Az effekt példánya; ismeretlen azonosítóra az alapértelmezett."""
    return EFFECTS.get(effect_id, EFFECTS[DEFAULT])(**kwargs)


def label(effect_id: str) -> str:
    """Az effekt neve az aktuális nyelven."""
    return t(f"fx.{effect_id}")
