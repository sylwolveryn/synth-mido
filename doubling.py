"""Oktáv duplázás ("két kéz") — Tk-tól független nyilvántartás.

Bekapcsolva minden játszott hanghoz ugyanaz a hang egy oktávval (12 félhanggal)
lejjebb és/vagy feljebb is megszólal. A nyilvántartás megjegyzi, melyik lenyomott
billentyű mely valódi hangokat indította, és hány lenyomott billentyűnek kell egy
valódi hang: így a beállítás menet közbeni váltása sem hagy lógó hangot, és a
közös hang (pl. C4 +1 mellett lenyomott C5) addig szól, amíg bármelyik billentyű kéri.
"""

from typing import Dict, List, Tuple

from piano_layout import FIRST_NOTE, LAST_NOTE

OFF, UP, DOWN, BOTH = "off", "up", "down", "both"
OFFSETS: Dict[str, Tuple[int, ...]] = {OFF: (), UP: (12,), DOWN: (-12,), BOTH: (-12, 12)}
LABELS: Dict[str, str] = {OFF: "Ki", UP: "+1 oktáv", DOWN: "−1 oktáv", BOTH: "±1 oktáv"}
DEFAULT_MODE = OFF


def targets(note: int, mode: str) -> List[int]:
    """A lenyomott hanghoz tartozó valódi hangok (a 88 billentyűn belül)."""
    notes = [note] + [note + off for off in OFFSETS.get(mode, ())]
    return [n for n in notes if FIRST_NOTE <= n <= LAST_NOTE]


class OctaveDoubler:
    def __init__(self, mode: str = DEFAULT_MODE):
        self.mode = mode if mode in OFFSETS else DEFAULT_MODE
        self._started: Dict[int, List[int]] = {}   # lenyomott hang -> általa indított valódi hangok
        self._count: Dict[int, int] = {}           # valódi hang -> hány lenyomott billentyű kéri

    def set_mode(self, mode: str) -> None:
        if mode in OFFSETS:
            self.mode = mode

    def press(self, note: int) -> List[int]:
        """Lenyomás: a megszólaltatandó valódi hangok (újraindítás is: a hang megszólal)."""
        if note in self._started:              # már le van nyomva — nincs új hang
            return []
        notes = targets(note, self.mode)
        self._started[note] = notes
        for n in notes:
            self._count[n] = self._count.get(n, 0) + 1
        return notes

    def release(self, note: int) -> List[int]:
        """Elengedés: azok a valódi hangok, amelyeket már egy lenyomott billentyű sem kér."""
        stop = []
        for n in self._started.pop(note, []):
            left = self._count.get(n, 0) - 1
            if left <= 0:
                self._count.pop(n, None)
                stop.append(n)
            else:
                self._count[n] = left
        return stop

    @property
    def sounding(self):
        return set(self._count)
