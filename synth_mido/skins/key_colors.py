"""Billentyű kiemelés színe hangforrásonként: billentyűzet / MIDI bemenet, lejátszás és a játékvezérlők
mind más színnel világítanak, hogy látszódjon, ki mit játszik.

A színek a skin palettájából (illetve egy élénk tartalék listából) jönnek; mindegyik legalább
`MIN_DISTANCE` távolságra van a már kiosztott színektől és a billentyűk alapszínétől, így minden
skinben megkülönböztethetők és láthatók.
"""

from typing import Dict, List, Tuple

from synth_mido.core import events
from synth_mido.core.gamepad import MAX_CONTROLLERS

MIN_DISTANCE = 80.0
CONTROLLER_HUES = ("#3ddc84", "#b388ff", "#ffd166", "#ff5252", "#00e5ff", "#ff80ab", "#c6ff00", "#ff9100",
                   "#7c4dff", "#00c853", "#2979ff", "#ffffff")


def _rgb(color: str) -> Tuple[int, int, int]:
    return int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)


def distance(a: str, b: str) -> float:
    return sum((x - y) ** 2 for x, y in zip(_rgb(a), _rgb(b))) ** 0.5


def _pick(candidates, avoid: List[str]) -> str:
    """Az első jelölt, amely minden kerülendő színtől elég messze van (különben a legtávolabbi)."""
    best, best_d = candidates[0], -1.0
    for c in candidates:
        d = min((distance(c, a) for a in avoid), default=999.0)
        if d >= MIN_DISTANCE:
            return c
        if d > best_d:
            best, best_d = c, d
    return best


def source_colors(p: dict) -> Dict[str, Tuple[str, str]]:
    """Hangforrás -> (fehér billentyű szín, fekete billentyű szín)."""
    user = (p["key_white_active"], p["key_black_active"])
    keys = [p["key_white"], p["key_black"]]
    taken = list(user)
    playback = _pick([p["sun_mid"], p["sun_top"], p["sun_bottom"], p["accent2"], p["accent"], *CONTROLLER_HUES],
                     taken + keys)
    taken.append(playback)
    colors = {events.USER: user, events.MIDI_IN: user, events.PLAYBACK: (playback, playback)}
    for n in range(MAX_CONTROLLERS):   # a többi forrás egy színnel világít fehér és fekete billentyűn is
        c = _pick(CONTROLLER_HUES, taken + keys)
        taken.append(c)
        colors[events.controller(n + 2)] = (c, c)
    return colors


def color_for(colors: Dict[str, Tuple[str, str]], source: str, black: bool) -> str:
    white_c, black_c = colors.get(source, colors[events.USER])
    return black_c if black else white_c
