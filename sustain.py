"""Kitartó (sustain) pedál — Tk-tól és kimenettől független nyilvántartás.

Lenyomott pedálnál az elengedett billentyűk hangja tovább szól; a pedál
felengedésekor minden így kitartott hang leáll. Így a pedál minden kimeneten
(MIDI eszköz, GS szintetizátor, beépített hanggenerátor) egyformán működik, és a
felvétel a ténylegesen szóló hosszt rögzíti.
"""

from typing import Callable, Set


class SustainPedal:
    def __init__(self, on_release: Callable[[int], None]):
        self._on_release = on_release
        self.down = False
        self.sustained: Set[int] = set()

    def key_down(self, note: int) -> None:
        """Újra lenyomott billentyű: már nem a pedál tartja, hanem a billentyű."""
        self.sustained.discard(note)

    def key_up(self, note: int) -> bool:
        """True, ha a hangot most kell leállítani; False, ha a pedál tartja."""
        if self.down:
            self.sustained.add(note)
            return False
        return True

    def press(self) -> None:
        self.down = True

    def release(self) -> None:
        """Pedál fel: minden kitartott hang leáll (hangmagasság szerint)."""
        self.down = False
        notes, self.sustained = sorted(self.sustained), set()
        for note in notes:
            self._on_release(note)
