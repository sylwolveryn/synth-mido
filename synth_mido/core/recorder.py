"""Felvétel — a játszott hangok rögzítése és JSON fájlba mentése a records/ mappába.

Egy felvétel formátuma (UTF-8 JSON), 2. verzió — minden hangnak saját hangszere van,
így egy felvételben több hangszer szólhat egyszerre (pl. visszajátszás + rájátszás):

    {
      "format": "synth-mido-record",
      "version": 2,
      "created": "2026-10-22T19:40:12",
      "instrument": {"name": "acoustic_grand_piano", "program": 0},
      "duration": 12.48,
      "notes": [{"note": 60, "velocity": 100, "start": 0.0, "duration": 0.42,
                 "instrument": {"name": "flute", "program": 73}}, ...]
    }

A felső szintű "instrument" a felvétel indításakor választott hangszer.

Az 1. verzióban (régi felvételek, daloskönyv) a hangoknak nincs "instrument" mezője;
ott a felső szintű hangszer csak alapértelmezés, a lejátszó felülírhatja.
"""

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, List, Optional

from synth_mido.core.i18n import t

RECORDS_DIR = Path(__file__).resolve().parents[2] / "records"  # a projekt gyökerében
FORMAT = "synth-mido-record"
V1 = 1        # egy hangszer, felülírható (régi felvételek, daloskönyv)
V2 = 2        # minden hangnak saját hangszere van
VERSION = V2  # az új felvételek verziója
VERSIONS = (V1, V2)
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
        self._held = {}  # (program, hang) -> (kezdet, hangerő, hangszer)
        self._notes = []
        self._instrument = {"name": "", "program": 0}  # induláskori hangszer
        self.current = {"name": "", "program": 0}       # az éppen választott hangszer (felhasználó, MIDI bemenet)
        self._created = ""

    def start(self, instrument_name: str, program: int) -> None:
        self._start_time = self._clock()
        self._stop_time = self._start_time
        self._held = {}
        self._notes = []
        self._instrument = {"name": instrument_name, "program": int(program)}
        self.current = dict(self._instrument)
        self._created = datetime.now().isoformat(timespec="seconds")
        self.is_recording = True

    def elapsed(self) -> float:
        end = self._clock() if self.is_recording else self._stop_time
        return max(end - self._start_time, 0.0)

    @property
    def note_count(self) -> int:
        return len(self._notes) + len(self._held)

    def set_instrument(self, instrument_name: str, program: int) -> None:
        """Hangszerváltás felvétel közben: a későbbi hangok már ezzel rögzülnek."""
        self.current = {"name": instrument_name, "program": int(program)}

    def note_on(self, note: int, velocity: int, instrument: Optional[dict] = None) -> None:
        """Hang kezdete; `instrument` nélkül az éppen választott hangszerrel (visszajátszott hangnál a sajátjával)."""
        if not self.is_recording:
            return
        instrument = dict(instrument or self.current)
        if velocity <= 0:
            self.note_off(note, instrument)
            return
        now = self._clock() - self._start_time
        key = (instrument["program"], int(note))
        if key in self._held:
            self._close(key, now)
        self._held[key] = (now, min(int(velocity), 127), instrument)

    def note_off(self, note: int, instrument: Optional[dict] = None) -> None:
        """Hang vége. Ha a megadott (vagy a jelenlegi) hangszerrel nem szól, az ugyanilyen magasságú
        hangot zárja — így a lenyomva tartott billentyű közbeni hangszerváltás sem hagy lógó hangot."""
        if not self.is_recording:
            return
        key = ((instrument or self.current)["program"], int(note))
        if key not in self._held:
            key = next((k for k in self._held if k[1] == note), None)
            if key is None:
                return
        self._close(key, self._clock() - self._start_time)

    def _close(self, key, end: float) -> None:
        start, velocity, instrument = self._held.pop(key)
        self._notes.append({
            "note": key[1], "velocity": velocity, "start": _r(start), "duration": _r(end - start),
            "instrument": instrument,
        })

    def stop(self) -> dict:
        """Felvétel leállítása; a még lenyomott hangokat a leállítás pillanatában zárja le."""
        if self.is_recording:
            self._stop_time = self._clock()
            end = self._stop_time - self._start_time
            for note in list(self._held):
                self._close(note, end)
            self.is_recording = False
        notes = sorted(self._notes, key=lambda n: (n["start"], n["note"], n["instrument"]["program"]))
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
        raise ValueError(t("rec.err.name_empty"))
    if name.upper() in _RESERVED_NAMES:
        raise ValueError(t("rec.err.name_reserved", name=name))
    return name


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


NOTE_KEYS = {
    V1: {"note", "velocity", "start", "duration"},
    V2: {"note", "velocity", "start", "duration", "instrument"},
}


def _is_instrument(value) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"name", "program"}
        and isinstance(value["name"], str)
        and _is_int(value["program"])
        and 0 <= value["program"] <= 127
    )


def note_instrument(record: dict, note: dict) -> Optional[dict]:
    """A hang saját hangszere (2. verzió); 1. verziónál None — ott a választott hangszer szól."""
    return note.get("instrument") if record.get("version") == V2 else None


def instruments_of(record: dict) -> List[dict]:
    """A felvételben szóló hangszerek első megszólalás szerint (1. verziónál a felvétel hangszere)."""
    if record.get("version") != V2:
        return [dict(record["instrument"])]
    seen = {}
    for n in record["notes"]:
        seen.setdefault(n["instrument"]["program"], n["instrument"])
    return [dict(i) for i in seen.values()] or [dict(record["instrument"])]


def validate_record(data) -> None:
    """Ellenőrzi a felvétel szerkezetét; hibára ValueError."""
    if not isinstance(data, dict):
        raise ValueError(t("rec.err.not_object"))
    if data.get("format") != FORMAT:
        raise ValueError(t("rec.err.format"))
    version = data.get("version")
    if isinstance(version, bool) or version not in VERSIONS:
        raise ValueError(t("rec.err.version", version=repr(version)))
    if not isinstance(data.get("created"), str):
        raise ValueError(t("rec.err.created"))
    if not _is_instrument(data.get("instrument")):
        raise ValueError(t("rec.err.instrument"))
    if not _is_num(data.get("duration")) or data["duration"] < 0:
        raise ValueError(t("rec.err.duration"))
    notes = data.get("notes")
    if not isinstance(notes, list):
        raise ValueError(t("rec.err.notes"))
    keys = NOTE_KEYS[version]
    for i, n in enumerate(notes):
        if (
            not isinstance(n, dict)
            or set(n) != keys
            or (version == V2 and not _is_instrument(n["instrument"]))
            or not _is_int(n["note"]) or not 0 <= n["note"] <= 127
            or not _is_int(n["velocity"]) or not 1 <= n["velocity"] <= 127
            or not _is_num(n["start"]) or n["start"] < 0
            or not _is_num(n["duration"]) or n["duration"] < 0
        ):
            raise ValueError(t("rec.err.note", index=i + 1))


def record_path(name: str, directory=None) -> Path:
    return Path(directory or RECORDS_DIR) / (sanitize_name(name) + EXTENSION)


def save_record(record: dict, name: str, directory=None, overwrite: bool = False) -> Path:
    """Felvétel mentése <directory>/<name>.json néven. Létező fájlra FileExistsError (ha nincs overwrite)."""
    validate_record(record)
    path = record_path(name, directory)
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # záró újsorral, ahogy a pre-commit end-of-file ellenőrzés várja
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_record(path) -> dict:
    """Felvétel betöltése és ellenőrzése; olvashatatlan / hibás fájlra ValueError."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(t("rec.err.unreadable", error=e)) from e
    validate_record(data)
    return data


@dataclass
class RecordInfo:
    path: Path
    name: str
    created: str = ""
    duration: float = 0.0
    note_count: int = 0
    instruments: List[str] = field(default_factory=list)
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
                instruments=[i["name"] for i in instruments_of(data)],
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
            raise ValueError(t("rec.err.not_record", path=path))
    deleted = 0
    for path in targets:
        try:
            path.unlink()
            deleted += 1
        except FileNotFoundError:
            pass
    return deleted
