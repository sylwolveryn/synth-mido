"""Felvétel visszajátszása — ütemezés és lejátszó (Tk-tól független).

A `build_schedule` a felvétel hangjaiból időrendi note_on / note_off eseményeket
készít; a `Player` ezeket a megadott `after` / `cancel` függvényekkel (Tk-ban
`root.after` / `root.after_cancel`) és egy órával szólaltatja meg.
"""

import time
from typing import Callable, Dict, List, NamedTuple, Optional

MIN_NOTE = 0.01  # mp — a 0 hosszú (pl. kerekített) hangok is hallhatók és elengedhetők legyenek


class Event(NamedTuple):
    time: float     # mp a lejátszás kezdetétől
    on: bool        # True = note_on, False = note_off
    note: int
    velocity: int


def build_schedule(record: dict) -> List[Event]:
    """Időrendi események. Azonos időpontban a note_off megelőzi a note_on-t.

    Ha ugyanaz a hang még szól, amikor újra megszólal, az előzőt az új kezdetéig
    rövidítjük, így a régi hang note_off-ja nem némítja el az újat; az azonos
    időben kezdődő ismétlésből csak az utolsó marad.
    """
    notes = sorted(record["notes"], key=lambda n: (n["start"], n["note"]))
    spans = []
    last_by_pitch: Dict[int, int] = {}
    for n in notes:
        start = float(n["start"])
        end = start + max(float(n["duration"]), MIN_NOTE)
        prev = last_by_pitch.get(n["note"])
        if prev is not None and spans[prev][1] > start:
            spans[prev][1] = start
        last_by_pitch[n["note"]] = len(spans)
        spans.append([start, end, n["note"], n["velocity"]])

    events = []
    for start, end, note, velocity in spans:
        if end <= start:
            continue
        events.append(Event(start, True, note, velocity))
        events.append(Event(end, False, note, 0))
    events.sort(key=lambda e: (e.time, e.on, e.note))
    return events


def default_instrument(record: dict, instruments: Dict[str, int]) -> str:
    """A felvétel hangszere a megadott listából: név szerint, különben program szám szerint, különben az első."""
    stored = record.get("instrument", {})
    if stored.get("name") in instruments:
        return stored["name"]
    for name, program in instruments.items():
        if program == stored.get("program"):
            return name
    return next(iter(instruments))


class Player:
    """Egy felvétel lejátszása időzítővel; egyszerre egy lejátszás."""

    def __init__(
        self,
        after: Callable[[int, Callable[[], None]], object],
        cancel: Callable[[object], None],
        on_note: Callable[[int, int, bool], None],
        on_finish: Optional[Callable[[], None]] = None,
        clock: Callable[[], float] = time.monotonic,
    ):
        self._after = after
        self._cancel = cancel
        self._on_note = on_note
        self._on_finish = on_finish
        self._clock = clock
        self._events: List[Event] = []
        self._index = 0
        self._start = 0.0
        self._job = None
        self.sounding = set()
        self.is_playing = False
        self.record_name = ""

    @property
    def duration(self) -> float:
        return self._events[-1].time if self._events else 0.0

    def play(self, record: dict, name: str = "") -> None:
        self.stop()
        self._events = build_schedule(record)
        self._index = 0
        self.record_name = name
        self.is_playing = True
        self._start = self._clock()
        self._tick()

    def _tick(self) -> None:
        self._job = None
        if not self.is_playing:
            return
        now = self._clock() - self._start
        while self._index < len(self._events) and self._events[self._index].time <= now:
            event = self._events[self._index]
            self._index += 1
            if event.on:
                self.sounding.add(event.note)
            else:
                self.sounding.discard(event.note)
            self._on_note(event.note, event.velocity, event.on)
        if self._index >= len(self._events):
            self.is_playing = False
            if self._on_finish:
                self._on_finish()
            return
        wait_ms = max(1, int((self._events[self._index].time - now) * 1000))
        self._job = self._after(wait_ms, self._tick)

    def stop(self) -> None:
        """Leállítás; a még szóló hangokat elengedi."""
        if self._job is not None:
            self._cancel(self._job)
            self._job = None
        self.is_playing = False
        for note in sorted(self.sounding):
            self._on_note(note, 0, False)
        self.sounding.clear()
