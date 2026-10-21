"""Oktáv duplázás ("két kéz") — Tk-tól független nyilvántartás.

Bekapcsolva minden játszott hanghoz ugyanaz a hang egy oktávval (12 félhanggal)
lejjebb és/vagy feljebb is megszólal. A nyilvántartás megjegyzi, melyik lenyomott
billentyű mely valódi hangokat indította, és hány lenyomott billentyűnek kell egy
valódi hang: így a beállítás menet közbeni váltása sem hagy lógó hangot, és a
közös hang (pl. C4 +1 mellett lenyomott C5) addig szól, amíg bármelyik billentyű kéri.
"""

from typing import Dict, List, Sequence, Tuple

from synth_mido.core.piano_layout import FIRST_NOTE, LAST_NOTE

OFF, UP, DOWN, BOTH = "off", "up", "down", "both"
OFFSETS: Dict[str, Tuple[int, ...]] = {OFF: (), UP: (12,), DOWN: (-12,), BOTH: (-12, 12)}
LABELS: Dict[str, str] = {OFF: "Ki", UP: "+1 oktáv", DOWN: "−1 oktáv", BOTH: "±1 oktáv"}
DEFAULT_MODE = OFF


def targets(note: int, mode: str, extra: Sequence[int] = ()) -> List[int]:
    """A lenyomott hanghoz tartozó valódi hangok (a 88 billentyűn belül): a hang, a duplázás oktávjai
    és a többoktávos választás eltolásai — ismétlés nélkül."""
    notes = []
    for n in [note] + [note + off for off in OFFSETS.get(mode, ())] + [note + off for off in extra]:
        if FIRST_NOTE <= n <= LAST_NOTE and n not in notes:
            notes.append(n)
    return notes


# --- többoktávos játék (TASK-017) ------------------------------------------------------

OCTAVE_BASES = tuple(range(12, 97, 12))   # C0 … C7: a billentyűzet lehetséges alaphangjai


def octave_label(base: int) -> str:
    return f"C{base // 12 - 1}"


class OctaveSelection:
    """A kiválasztott oktávok: a billentyűzet oktávja (X / C) mindig benne van, a többit a játékos jelöli be."""

    def __init__(self, base: int):
        self.base = base
        self.extras = set()

    def set_base(self, base: int) -> None:
        self.base = base

    def toggle(self, octave: int) -> bool:
        """Be / ki jelölés; a billentyűzet oktávja nem vehető ki (False)."""
        if octave == self.base or octave not in OCTAVE_BASES:
            return False
        self.extras ^= {octave}
        return True

    def is_selected(self, octave: int) -> bool:
        return octave == self.base or octave in self.extras

    def selected(self) -> List[int]:
        return sorted(self.extras | {self.base})

    def offsets(self) -> Tuple[int, ...]:
        """A billentyűzet oktávjához képesti eltolások (félhang) a többi kiválasztott oktávra."""
        return tuple(o - self.base for o in sorted(self.extras) if o != self.base)

    def label(self) -> str:
        return " · ".join(octave_label(o) for o in self.selected())


class OctaveDoubler:
    def __init__(self, mode: str = DEFAULT_MODE):
        self.mode = mode if mode in OFFSETS else DEFAULT_MODE
        self._started: Dict[int, List[int]] = {}   # lenyomott hang -> általa indított valódi hangok
        self._count: Dict[int, int] = {}           # valódi hang -> hány lenyomott billentyű kéri
        self.extra_offsets: Tuple[int, ...] = ()   # többoktávos játék eltolásai (TASK-017)

    def set_mode(self, mode: str) -> None:
        if mode in OFFSETS:
            self.mode = mode

    def set_extra_offsets(self, offsets: Sequence[int]) -> None:
        self.extra_offsets = tuple(offsets)

    def press(self, note: int) -> List[int]:
        """Lenyomás: a megszólaltatandó valódi hangok (újraindítás is: a hang megszólal)."""
        if note in self._started:              # már le van nyomva — nincs új hang
            return []
        notes = targets(note, self.mode, self.extra_offsets)
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
