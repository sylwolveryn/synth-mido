"""Felvétel — a játszott hangok rögzítése és JSON fájlba mentése a records/ mappába.

Egy felvétel formátuma (UTF-8 JSON):

    {
      "format": "synth-mido-record",
      "version": 1,
      "created": "2026-10-21T19:40:12",
      "instrument": {"name": "acoustic_grand_piano", "program": 0},
      "duration": 12.48,
      "notes": [{"note": 60, "velocity": 100, "start": 0.0, "duration": 0.42}, ...]
    }

A hangszer csak alapértelmezés a visszajátszáshoz; a lejátszó felülírhatja.
"""

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, List, Optional

RECORDS_DIR = Path(__file__).resolve().parents[2] / "records"  # a projekt gyökerében
FORMAT = "synth-mido-record"
VERSION = 1
EXTENSION = ".json"
DEFAULT_PREFIX = "felvetel_"

_ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _r(seconds: float) -> float:
    """Másodperc kerekítése ezredmásodpercre."""
    return round(max(seconds, 0.0), 3)


class Recorder:
    """Hangok rögzítése időbélyeggel. Tk-tól független, az óra tesztben cserélhető."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self.is_recording = False
        self._start_time = 0.0
        self._stop_time = 0.0
        self._held = {}  # hang -> (kezdet, hangerő)
        self._notes = []
        self._instrument = {"name": "", "program": 0}
        self._created = ""

    def start(self, instrument_name: str, program: int) -> None:
        self._start_time = self._clock()
        self._stop_time = self._start_time
        self._held = {}
        self._notes = []
        self._instrument = {"name": instrument_name, "program": int(program)}
        self._created = datetime.now().isoformat(timespec="seconds")
        self.is_recording = True

    def elapsed(self) -> float:
        end = self._clock() if self.is_recording else self._stop_time
        return max(end - self._start_time, 0.0)

    @property
    def note_count(self) -> int:
        return len(self._notes) + len(self._held)

    def note_on(self, note: int, velocity: int) -> None:
        if not self.is_recording:
            return
        if velocity <= 0:
            self.note_off(note)
            return
        now = self._clock() - self._start_time
        if note in self._held:
            self._close(note, now)
        self._held[note] = (now, min(int(velocity), 127))

    def note_off(self, note: int) -> None:
        if not self.is_recording or note not in self._held:
            return
        self._close(note, self._clock() - self._start_time)

    def _close(self, note: int, end: float) -> None:
        start, velocity = self._held.pop(note)
        self._notes.append(
            {"note": int(note), "velocity": velocity, "start": _r(start), "duration": _r(end - start)}
        )

    def stop(self) -> dict:
        """Felvétel leállítása; a még lenyomott hangokat a leállítás pillanatában zárja le."""
        if self.is_recording:
            self._stop_time = self._clock()
            end = self._stop_time - self._start_time
            for note in list(self._held):
                self._close(note, end)
            self.is_recording = False
        notes = sorted(self._notes, key=lambda n: (n["start"], n["note"]))
        return {
            "format": FORMAT,
            "version": VERSION,
            "created": self._created,
            "instrument": dict(self._instrument),
            "duration": _r(self._stop_time - self._start_time),
            "notes": notes,
        }


def default_name(now: Optional[datetime] = None) -> str:
    return DEFAULT_PREFIX + (now or datetime.now()).strftime("%Y%m%d_%H%M%S")


def sanitize_name(name: str) -> str:
    """Felhasználói név -> biztonságos fájlnév (kiterjesztés nélkül). Üres / foglalt névre ValueError."""
    name = (name or "").strip()
    if name.lower().endswith(EXTENSION):
        name = name[: -len(EXTENSION)]
    name = _ILLEGAL_CHARS.sub("_", name).strip().rstrip(".")
    if not name:
        raise ValueError("Adj meg egy nevet a felvételnek.")
    if name.upper() in _RESERVED_NAMES:
        raise ValueError(f"A(z) „{name}” név nem használható fájlnévként.")
    return name


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_record(data) -> None:
    """Ellenőrzi a felvétel szerkezetét; hibára ValueError."""
    if not isinstance(data, dict):
        raise ValueError("A felvétel nem JSON objektum.")
    if data.get("format") != FORMAT:
        raise ValueError("Ismeretlen fájlformátum.")
    if data.get("version") != VERSION:
        raise ValueError(f"Nem támogatott verzió: {data.get('version')!r}.")
    if not isinstance(data.get("created"), str):
        raise ValueError("Hiányzik a létrehozás ideje.")
    instrument = data.get("instrument")
    if (
        not isinstance(instrument, dict)
        or not isinstance(instrument.get("name"), str)
        or not _is_int(instrument.get("program"))
        or not 0 <= instrument["program"] <= 127
    ):
        raise ValueError("Hibás hangszer adat.")
    if not _is_num(data.get("duration")) or data["duration"] < 0:
        raise ValueError("Hibás felvétel hossz.")
    notes = data.get("notes")
    if not isinstance(notes, list):
        raise ValueError("Hiányzik a hangok listája.")
    for i, n in enumerate(notes):
        if (
            not isinstance(n, dict)
            or set(n) != {"note", "velocity", "start", "duration"}
            or not _is_int(n["note"]) or not 0 <= n["note"] <= 127
            or not _is_int(n["velocity"]) or not 1 <= n["velocity"] <= 127
            or not _is_num(n["start"]) or n["start"] < 0
            or not _is_num(n["duration"]) or n["duration"] < 0
        ):
            raise ValueError(f"Hibás hang a(z) {i + 1}. helyen.")


def record_path(name: str, directory=None) -> Path:
    return Path(directory or RECORDS_DIR) / (sanitize_name(name) + EXTENSION)


def save_record(record: dict, name: str, directory=None, overwrite: bool = False) -> Path:
    """Felvétel mentése <directory>/<name>.json néven. Létező fájlra FileExistsError (ha nincs overwrite)."""
    validate_record(record)
    path = record_path(name, directory)
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_record(path) -> dict:
    """Felvétel betöltése és ellenőrzése; olvashatatlan / hibás fájlra ValueError."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"A fájl nem olvasható: {e}") from e
    validate_record(data)
    return data


@dataclass
class RecordInfo:
    path: Path
    name: str
    created: str = ""
    duration: float = 0.0
    note_count: int = 0
    instrument: str = ""
    error: Optional[str] = None


def list_records(directory=None) -> List[RecordInfo]:
    """A mappa összes felvétele, legújabb elöl. A hibás fájlok is szerepelnek (error), hogy törölhetők legyenek."""
    folder = Path(directory or RECORDS_DIR)
    if not folder.is_dir():
        return []
    items = []
    for path in folder.glob("*" + EXTENSION):
        if not path.is_file():
            continue
        try:
            data = load_record(path)
            items.append(RecordInfo(
                path=path,
                name=path.stem,
                created=data["created"],
                duration=data["duration"],
                note_count=len(data["notes"]),
                instrument=data["instrument"]["name"],
            ))
        except ValueError as e:
            items.append(RecordInfo(path=path, name=path.stem, error=str(e)))
    items.sort(key=lambda r: (r.created or "", r.path.stat().st_mtime), reverse=True)
    return items


def delete_records(paths: Iterable, directory=None) -> int:
    """A megadott felvételek törlése; csak a mappán belüli .json fájlokat törli. Visszaadja a törölt darabszámot."""
    folder = Path(directory or RECORDS_DIR).resolve()
    targets = [Path(p).resolve() for p in paths]
    for path in targets:
        if path.parent != folder or path.suffix != EXTENSION:
            raise ValueError(f"Nem felvétel fájl: {path}")
    deleted = 0
    for path in targets:
        try:
            path.unlink()
            deleted += 1
        except FileNotFoundError:
            pass
    return deleted
