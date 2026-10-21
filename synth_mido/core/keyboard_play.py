"""Zongorázás a számítógép billentyűzetével (Tk-tól független).

Elrendezés (a zenei programokban megszokott két sor):

    W E   T Y/Z U   O P            <- fekete billentyűk
   A S D F G H J K L É/; Á/'      <- fehér billentyűk: C … F (egy oktávval feljebb)

Amerikai QWERTY és magyar QWERTZ kiosztáson is ugyanazokon a fizikai gombokon
szól: a Y és Z helye fel van cserélve, ezért mindkettő a G#; a ; / É és ' / Á
ugyanannak a gombnak a két kiosztás szerinti neve.
"""

from typing import Callable, Dict, Optional

from synth_mido.core.piano_layout import FIRST_NOTE, LAST_NOTE, MIDDLE_C

KEYMAP: Dict[str, int] = {
    "a": 0, "w": 1, "s": 2, "e": 3, "d": 4, "f": 5, "t": 6, "g": 7,
    "y": 8, "z": 8, "h": 9, "u": 10, "j": 11, "k": 12, "o": 13, "l": 14, "p": 15,
    # a Tk verziótól függően a keysym a név (eacute) vagy maga a karakter (é)
    "semicolon": 16, ";": 16, "eacute": 16, "é": 16,
    "apostrophe": 17, "'": 17, "aacute": 17, "á": 17,
}
DEFAULT_BASE = MIDDLE_C
RELEASE_DELAY_MS = 30  # X11 billentyűismétlés: elengedés + azonnali lenyomás párok kiszűrése

# Oktávváltás: X le, C fel (mindkét kiosztáson ugyanott, hangot nem játszanak)
OCTAVE_KEYS: Dict[str, int] = {"x": -1, "c": 1}
MIN_BASE = 12   # C0: így az A0 (H gomb) még elérhető
MAX_BASE = 96   # C7: így a C8 (K gomb) még elérhető

PEDAL_KEYS = {"space", " "}  # kitartó pedál

# Megjelenített betű félhangonként (magyar QWERTZ szerint)
DISPLAY_LABELS: Dict[int, str] = {
    0: "A", 1: "W", 2: "S", 3: "E", 4: "D", 5: "F", 6: "T", 7: "G", 8: "Z", 9: "H",
    10: "U", 11: "J", 12: "K", 13: "O", 14: "L", 15: "P", 16: "É", 17: "Á",
}
SPAN = max(KEYMAP.values())


def normalize(keysym: str) -> str:
    return keysym.lower()


def note_for(keysym: str, base: int = DEFAULT_BASE) -> Optional[int]:
    """A billentyűhöz tartozó hang, ha van és a 88 billentyűs tartományba esik."""
    offset = KEYMAP.get(normalize(keysym))
    if offset is None:
        return None
    note = base + offset
    return note if FIRST_NOTE <= note <= LAST_NOTE else None


class KeyboardPlayer:
    """Lenyomott billentyűk követése: hang indítás / elengedés, billentyűismétlés nélkül."""

    def __init__(
        self,
        after: Callable[[int, Callable[[], None]], object],
        cancel: Callable[[object], None],
        on_note: Callable[[int, bool], None],
        base: int = DEFAULT_BASE,
        release_delay_ms: int = RELEASE_DELAY_MS,
        on_range_change: Optional[Callable[[], None]] = None,
        on_pedal: Optional[Callable[[bool], None]] = None,
    ):
        self._after = after
        self._cancel = cancel
        self._on_range_change = on_range_change
        self._on_pedal = on_pedal
        self._octave_held = set()
        self.pedal_held = False
        self._pedal_job = None
        self._on_note = on_note
        self.base = base
        self._delay = release_delay_ms
        self.held: Dict[str, Optional[int]] = {}   # billentyű -> szóló hang (None: tartományon kívül)
        self._pending: Dict[str, object] = {}      # billentyű -> késleltetett elengedés

    def handles(self, keysym: str) -> bool:
        key = normalize(keysym)
        return key in KEYMAP or key in OCTAVE_KEYS or key in PEDAL_KEYS

    # --- pedál ------------------------------------------------------------------

    def _pedal_press(self) -> None:
        if self._pedal_job is not None:     # elengedés + azonnali lenyomás = ismétlés
            self._cancel(self._pedal_job)
            self._pedal_job = None
            return
        if self.pedal_held:
            return
        self.pedal_held = True
        if self._on_pedal:
            self._on_pedal(True)

    def _pedal_release(self) -> None:
        if self.pedal_held and self._pedal_job is None:
            self._pedal_job = self._after(self._delay, self._pedal_release_now)

    def _pedal_release_now(self) -> None:
        self._pedal_job = None
        if self.pedal_held:
            self.pedal_held = False
            if self._on_pedal:
                self._on_pedal(False)

    # --- oktávváltás ------------------------------------------------------------

    def shift(self, octaves: int) -> bool:
        """Tartomány eltolása; False, ha a szélen már nem lehet tovább."""
        new_base = min(max(self.base + 12 * octaves, MIN_BASE), MAX_BASE)
        if new_base == self.base:
            return False
        self.base = new_base
        if self._on_range_change:
            self._on_range_change()
        return True

    def range_notes(self):
        """A billentyűzettel elérhető legalsó és legfelső hang (A0–C8-ra vágva)."""
        return max(self.base, FIRST_NOTE), min(self.base + SPAN, LAST_NOTE)

    def key_labels(self) -> Dict[int, str]:
        """hang -> betű a jelenlegi tartományban (csak a 88 billentyűn belül)."""
        return {
            self.base + offset: label
            for offset, label in DISPLAY_LABELS.items()
            if FIRST_NOTE <= self.base + offset <= LAST_NOTE
        }

    # --- lenyomás / elengedés ---------------------------------------------------

    def press(self, keysym: str) -> bool:
        """True, ha a billentyű zongora vagy oktáv billentyű (akkor is, ha ismétlés volt)."""
        key = normalize(keysym)
        if key in PEDAL_KEYS:
            self._pedal_press()
            return True
        if key in OCTAVE_KEYS:
            if key not in self._octave_held:
                self._octave_held.add(key)
                self.shift(OCTAVE_KEYS[key])
            return True
        if key not in KEYMAP:
            return False
        job = self._pending.pop(key, None)
        if job is not None:          # elengedés + azonnali újra lenyomás = ismétlés
            self._cancel(job)
            return True
        if key in self.held:         # lenyomva tartott billentyű ismétlése
            return True
        note = note_for(key, self.base)
        self.held[key] = note
        if note is not None:
            self._on_note(note, True)
        return True

    def release(self, keysym: str) -> bool:
        key = normalize(keysym)
        if key in PEDAL_KEYS:
            self._pedal_release()
            return True
        if key in OCTAVE_KEYS:
            self._octave_held.discard(key)
            return True
        if key not in self.held:
            return key in KEYMAP
        if key not in self._pending:
            self._pending[key] = self._after(self._delay, lambda: self._release_now(key))
        return True

    def _release_now(self, key: str) -> None:
        self._pending.pop(key, None)
        note = self.held.pop(key, None)
        if note is not None:
            self._on_note(note, False)

    def release_all(self) -> None:
        for job in self._pending.values():
            self._cancel(job)
        self._pending.clear()
        self._octave_held.clear()
        for key in list(self.held):
            self._release_now(key)
        if self._pedal_job is not None:
            self._cancel(self._pedal_job)
            self._pedal_job = None
        self._pedal_release_now()

    @property
    def sounding(self):
        return {n for n in self.held.values() if n is not None}
