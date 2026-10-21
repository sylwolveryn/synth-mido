"""Felvétel visszajátszása — ütemezés és lejátszó (Tk-tól független).

A `build_schedule` a felvétel hangjaiból időrendi note_on / note_off eseményeket
készít; a `Player` ezeket a megadott `after` / `cancel` függvényekkel (Tk-ban
`root.after` / `root.after_cancel`) és egy órával szólaltatja meg.

Minden hanghoz tartozik egy hangszer: 2. verziójú felvételnél a hang saját hangszere
({"name", "program"}), 1. verziónál None — ilyenkor a felhasználó választott hangszere szól.
"""

import time
from bisect import bisect_left
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple

from synth_mido.core.recorder import note_instrument

MIN_NOTE = 0.01  # mp — a 0 hosszú (pl. kerekített) hangok is hallhatók és elengedhetők legyenek


class Event(NamedTuple):
    time: float     # mp a lejátszás kezdetétől
    on: bool        # True = note_on, False = note_off
    note: int
    velocity: int
    instrument: Optional[dict] = None  # a hang hangszere (2. verzió), különben None


def _program(instrument: Optional[dict]) -> int:
    return -1 if instrument is None else instrument["program"]


def build_schedule(record: dict) -> List[Event]:
    """Időrendi események. Azonos időpontban a note_off megelőzi a note_on-t.

    Ha ugyanaz a hang ugyanazon a hangszeren még szól, amikor újra megszólal, az
    előzőt az új kezdetéig rövidítjük, így a régi hang note_off-ja nem némítja el az
    újat; az azonos időben kezdődő ismétlésből csak az utolsó marad. Különböző
    hangszerek azonos hangjai egymástól függetlenül szólnak.
    """
    events = []
    for span in build_spans(record):
        events.append(Event(span.start, True, span.note, span.velocity, span.instrument))
        events.append(Event(span.end, False, span.note, 0, span.instrument))
    events.sort(key=lambda e: (e.time, e.on, e.note, _program(e.instrument)))
    return events


class Span(NamedTuple):
    start: float
    end: float
    note: int
    velocity: int
    instrument: Optional[dict] = None


def build_spans(record: dict) -> List[Span]:
    """A felvétel hangjai [start, end) szakaszként, az ütemezés szabályai szerint javítva."""
    notes = sorted(record["notes"], key=lambda n: (n["start"], n["note"]))
    spans = []
    last_by_voice: Dict[Tuple[int, int], int] = {}
    for n in notes:
        instrument = note_instrument(record, n)
        start = float(n["start"])
        end = start + max(float(n["duration"]), MIN_NOTE)
        voice = (_program(instrument), n["note"])
        prev = last_by_voice.get(voice)
        if prev is not None and spans[prev][1] > start:
            spans[prev][1] = start
        last_by_voice[voice] = len(spans)
        spans.append([start, end, n["note"], n["velocity"], instrument])
    return [Span(*s) for s in spans if s[1] > s[0]]


def default_instrument(record: dict, instruments: Dict[str, int]) -> str:
    """A felvétel hangszere a megadott listából: név szerint, különben program szám szerint, különben az első."""
    stored = record.get("instrument", {})
    if stored.get("name") in instruments:
        return stored["name"]
    for name, program in instruments.items():
        if program == stored.get("program"):
            return name
    return next(iter(instruments))


DRUM_CHANNEL = 9   # General MIDI: a 10. csatorna dob, hangszernek nem használjuk
RECORD_CHANNELS = tuple(c for c in range(1, 16) if c != DRUM_CHANNEL)


def assign_channels(instruments: List[dict]) -> Dict[int, int]:
    """Program -> MIDI csatorna egy több hangszeres felvételhez. A 0. csatorna a felhasználóé
    (a választott hangszer), így rájátszáskor nem keverednek; 14-nél több hangszer csatornát oszt."""
    channels: Dict[int, int] = {}
    for instrument in instruments:
        program = instrument["program"]
        if program not in channels:
            channels[program] = RECORD_CHANNELS[len(channels) % len(RECORD_CHANNELS)]
    return channels


STOPPED = "stopped"
PLAYING = "playing"
PAUSED = "paused"
SPEEDS = (0.5, 0.75, 1.0, 1.25, 1.5, 2.0)


class Player:
    """Egy betöltött felvétel lejátszója: lejátszás / szünet / leállítás, ugrás és sebesség.

    A pozíció a felvétel idejében (mp) értendő, a sebességtől függetlenül. Az `on_note`
    (hang, hangerő, szól-e, hangszer) hívást kap; a hangszer 1. verziónál None.
    """

    def __init__(
        self,
        after: Callable[[int, Callable[[], None]], object],
        cancel: Callable[[object], None],
        on_note: Callable[[int, int, bool, Optional[dict]], None],
        on_finish: Optional[Callable[[], None]] = None,
        clock: Callable[[], float] = time.monotonic,
    ):
        self._after = after
        self._cancel = cancel
        self._on_note = on_note
        self._on_finish = on_finish
        self._clock = clock
        self._events: List[Event] = []
        self._spans: List[Span] = []
        self._index = 0
        self._base_pos = 0.0     # pozíció a legutóbbi (újra)indításkor
        self._base_clock = 0.0   # óra a legutóbbi (újra)indításkor
        self._pos = 0.0          # pozíció, ha nem szól
        self._job = None
        self._voices: Dict[Tuple[int, int], Tuple[int, Optional[dict]]] = {}  # (program, hang) -> (hangerő, hangszer)
        self.state = STOPPED
        self.speed = 1.0
        self.record_name = ""

    # --- állapot ------------------------------------------------------------

    @property
    def is_playing(self) -> bool:
        return self.state == PLAYING

    @property
    def is_paused(self) -> bool:
        return self.state == PAUSED

    @property
    def is_loaded(self) -> bool:
        return bool(self._events)

    @property
    def sounding(self) -> set:
        """Az éppen szóló hangok magassága."""
        return {note for _, note in self._voices}

    def sounding_voices(self) -> List[Tuple[int, int, Optional[dict]]]:
        """Az éppen szóló hangok (hang, hangerő, hangszer) — pl. lejátszás közben indított felvételhez."""
        return [(note, vel, inst) for (_, note), (vel, inst) in sorted(self._voices.items())]

    @property
    def duration(self) -> float:
        return self._events[-1].time if self._events else 0.0

    def position(self) -> float:
        if self.state == PLAYING:
            pos = self._base_pos + (self._clock() - self._base_clock) * self.speed
            return min(pos, self.duration)
        return self._pos

    # --- vezérlés -----------------------------------------------------------

    def load(self, record: dict, name: str = "") -> None:
        """Felvétel betöltése (az elejére állítva, lejátszás nélkül)."""
        self.stop()
        self._spans = build_spans(record)
        self._events = build_schedule(record)
        self.record_name = name
        self._pos = 0.0

    def play(self, record: dict, name: str = "") -> None:
        """Betöltés és lejátszás az elejéről."""
        self.load(record, name)
        if not self._events:
            if self._on_finish:
                self._on_finish()
            return
        self._start_at(0.0)

    def play_pause(self) -> None:
        if self.state == PLAYING:
            self.pause()
        elif self._events:
            self._start_at(0.0 if self._pos >= self.duration else self._pos)

    def pause(self) -> None:
        if self.state != PLAYING:
            return
        self._pos = self.position()
        self._halt()
        self.state = PAUSED

    def stop(self) -> None:
        """Leállítás és visszatekerés az elejére; a felvétel betöltve marad."""
        self._halt()
        self._pos = 0.0
        self.state = STOPPED

    def seek(self, position: float) -> None:
        """Ugrás a megadott pozícióra (lejátszás közben, szünetben vagy leállítva)."""
        if not self._events:
            return
        position = min(max(position, 0.0), self.duration)
        if self.state == PLAYING:
            self._halt()
            self._start_at(position)
        else:
            self._pos = position
            self.state = PAUSED

    def set_speed(self, speed: float) -> None:
        if speed <= 0:
            raise ValueError("A sebességnek pozitívnak kell lennie.")
        if self.state == PLAYING:
            self._base_pos = self.position()
            self._base_clock = self._clock()
            self.speed = speed
            self._reschedule()
        else:
            self.speed = speed

    # --- belső ----------------------------------------------------------------

    def _halt(self) -> None:
        if self._job is not None:
            self._cancel(self._job)
            self._job = None
        for (_, note), (_, instrument) in sorted(self._voices.items()):
            self._on_note(note, 0, False, instrument)
        self._voices.clear()

    def _start_at(self, position: float) -> None:
        """Lejátszás indítása `position`-ből: az ott épp szóló hangok újraindulnak."""
        self.state = PLAYING
        self._base_pos = position
        self._base_clock = self._clock()
        self._index = bisect_left([e.time for e in self._events], position)
        for span in self._spans:
            if span.start < position < span.end:
                self._voices[(_program(span.instrument), span.note)] = (span.velocity, span.instrument)
                self._on_note(span.note, span.velocity, True, span.instrument)
        self._tick()

    def _reschedule(self) -> None:
        if self._job is not None:
            self._cancel(self._job)
            self._job = None
        self._tick()

    def _tick(self) -> None:
        self._job = None
        if self.state != PLAYING:
            return
        now = self._base_pos + (self._clock() - self._base_clock) * self.speed
        while self._index < len(self._events) and self._events[self._index].time <= now:
            event = self._events[self._index]
            self._index += 1
            voice = (_program(event.instrument), event.note)
            if event.on:
                self._voices[voice] = (event.velocity, event.instrument)
                self._on_note(event.note, event.velocity, True, event.instrument)
            elif voice in self._voices:
                del self._voices[voice]
                self._on_note(event.note, 0, False, event.instrument)
        if self._index >= len(self._events):
            self._halt()
            self._pos = self.duration
            self.state = STOPPED
            if self._on_finish:
                self._on_finish()
            return
        wait = (self._events[self._index].time - now) / self.speed
        self._job = self._after(max(1, int(wait * 1000)), self._tick)
