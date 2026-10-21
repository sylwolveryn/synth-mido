"""A 88 billentyűs zongora geometriája (Tk-tól független).

A0 (MIDI 21) – C8 (MIDI 108): 52 fehér és 36 fekete billentyű. A fehér billentyűk
egyenletesen töltik ki a szélességet, a fekete billentyűk a két szomszédos fehér
határára kerülnek.
"""

from typing import List, NamedTuple, Optional

FIRST_NOTE = 21    # A0
LAST_NOTE = 108    # C8
MIDDLE_C = 60      # C4
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
BLACK_PITCH_CLASSES = {1, 3, 6, 8, 10}
BLACK_WIDTH = 0.6    # a fehér billentyű szélességéhez képest
BLACK_HEIGHT = 0.62  # a billentyűzet magasságához képest


class Key(NamedTuple):
    note: int
    black: bool
    x0: float
    y0: float
    x1: float
    y1: float


def is_black(note: int) -> bool:
    return note % 12 in BLACK_PITCH_CLASSES


def note_label(note: int) -> str:
    return f"{NOTE_NAMES[note % 12]}{note // 12 - 1}"


def white_notes(first: int = FIRST_NOTE, last: int = LAST_NOTE) -> List[int]:
    return [n for n in range(first, last + 1) if not is_black(n)]


def label_notes(first: int = FIRST_NOTE, last: int = LAST_NOTE) -> List[int]:
    """A feliratozott billentyűk: a C-k (C1 … C8)."""
    return [n for n in range(first, last + 1) if n % 12 == 0]


def layout(width: float, height: float, first: int = FIRST_NOTE, last: int = LAST_NOTE) -> List[Key]:
    """Billentyű téglalapok; előbb a fehérek, utána a feketék (rajzolási sorrend)."""
    whites = white_notes(first, last)
    white_w = width / len(whites)
    index = {note: i for i, note in enumerate(whites)}
    keys = [Key(n, False, i * white_w, 0.0, (i + 1) * white_w, height) for i, n in enumerate(whites)]
    black_w = white_w * BLACK_WIDTH
    black_h = height * BLACK_HEIGHT
    for note in range(first, last + 1):
        if is_black(note):
            cx = (index[note - 1] + 1) * white_w  # a bal oldali fehér jobb széle
            keys.append(Key(note, True, cx - black_w / 2, 0.0, cx + black_w / 2, black_h))
    return keys


def key_at(keys: List[Key], x: float, y: float) -> Optional[int]:
    """A pontban lévő billentyű hangja (a fekete billentyűk vannak felül)."""
    for key in sorted(keys, key=lambda k: not k.black):
        if key.x0 <= x < key.x1 and key.y0 <= y < key.y1:
            return key.note
    return None
