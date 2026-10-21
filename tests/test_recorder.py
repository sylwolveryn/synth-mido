"""Tesztek a recorder modulhoz: felvétel szerkezete, mentés, betöltés, listázás, törlés.

Futtatás:  python -m unittest test_recorder -v
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from synth_mido.core import recorder


class FakeClock:
    def __init__(self, t: float = 100.0):
        self.t = t

    def __call__(self) -> float:
        return self.t

    def advance(self, seconds: float) -> None:
        self.t += seconds


def make_record() -> dict:
    """Egy rövid felvétel: C4 és E4, a G4 a leállításig nyomva marad."""
    clock = FakeClock()
    rec = recorder.Recorder(clock=clock)
    rec.start("acoustic_grand_piano", 0)
    rec.note_on(60, 100)
    clock.advance(0.5)
    rec.note_on(64, 80)
    clock.advance(0.25)
    rec.note_off(60)
    clock.advance(0.25)
    rec.note_on(64, 0)  # note_on 0 hangerővel = note_off
    rec.note_on(67, 90)
    clock.advance(1.0)
    return rec.stop()


class RecordShapeTests(unittest.TestCase):
    def setUp(self):
        self.record = make_record()

    def test_top_level_keys(self):
        self.assertEqual(
            set(self.record), {"format", "version", "created", "instrument", "duration", "notes"}
        )
        self.assertEqual(self.record["format"], recorder.FORMAT)
        self.assertEqual(self.record["version"], recorder.VERSION)
        datetime.fromisoformat(self.record["created"])

    def test_instrument_stored(self):
        self.assertEqual(self.record["instrument"], {"name": "acoustic_grand_piano", "program": 0})

    def test_notes_have_timing_and_velocity(self):
        piano = {"name": "acoustic_grand_piano", "program": 0}
        self.assertEqual(self.record["notes"], [
            {"note": 60, "velocity": 100, "start": 0.0, "duration": 0.75, "instrument": piano},
            {"note": 64, "velocity": 80, "start": 0.5, "duration": 0.5, "instrument": piano},
            {"note": 67, "velocity": 90, "start": 1.0, "duration": 1.0, "instrument": piano},
        ])
        self.assertEqual(self.record["duration"], 2.0)

    def test_record_is_valid_and_json_serialisable(self):
        recorder.validate_record(self.record)
        self.assertEqual(json.loads(json.dumps(self.record)), self.record)

    def test_retriggered_note_closes_previous(self):
        clock = FakeClock()
        rec = recorder.Recorder(clock=clock)
        rec.start("piano", 0)
        rec.note_on(60, 100)
        clock.advance(0.2)
        rec.note_on(60, 50)
        clock.advance(0.3)
        rec.note_off(60)
        notes = rec.stop()["notes"]
        self.assertEqual([(n["start"], n["duration"], n["velocity"]) for n in notes], [(0.0, 0.2, 100), (0.2, 0.3, 50)])

    def test_counters_and_idle_events(self):
        clock = FakeClock()
        rec = recorder.Recorder(clock=clock)
        rec.note_on(60, 100)  # nincs felvétel -> figyelmen kívül
        self.assertEqual(rec.note_count, 0)
        rec.start("piano", 0)
        rec.note_on(60, 100)
        clock.advance(3)
        self.assertEqual(rec.note_count, 1)
        self.assertAlmostEqual(rec.elapsed(), 3)
        rec.stop()
        self.assertFalse(rec.is_recording)

    def test_empty_recording(self):
        rec = recorder.Recorder(clock=FakeClock())
        rec.start("piano", 0)
        self.assertEqual(rec.stop()["notes"], [])


class NameTests(unittest.TestCase):
    def test_default_name_pattern(self):
        self.assertEqual(recorder.default_name(datetime(2026, 10, 21, 9, 5, 3)), "felvetel_20261021_090503")

    def test_sanitize(self):
        self.assertEqual(recorder.sanitize_name("  dal.json "), "dal")
        self.assertEqual(recorder.sanitize_name('a/b:c*?'), "a_b_c__")
        self.assertEqual(recorder.sanitize_name("Esti dal – 2"), "Esti dal – 2")

    def test_sanitize_rejects_empty_and_reserved(self):
        for bad in ("", "   ", ".json", "CON", "lpt1"):
            with self.assertRaises(ValueError, msg=bad):
                recorder.sanitize_name(bad)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "records"
        self.record = make_record()

    def test_save_creates_json_file_in_records_dir(self):
        path = recorder.save_record(self.record, "elso", self.dir)
        self.assertEqual(path, self.dir / "elso.json")
        self.assertTrue(path.is_file())
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.record)

    def test_saved_file_ends_with_newline(self):
        path = recorder.save_record(self.record, "ujsor", self.dir)
        self.assertTrue(path.read_text(encoding="utf-8").endswith("}\n"))

    def test_save_load_round_trip(self):
        path = recorder.save_record(self.record, "kor", self.dir)
        self.assertEqual(recorder.load_record(path), self.record)

    def test_save_refuses_overwrite_unless_asked(self):
        recorder.save_record(self.record, "dal", self.dir)
        with self.assertRaises(FileExistsError):
            recorder.save_record(self.record, "dal", self.dir)
        recorder.save_record(self.record, "dal", self.dir, overwrite=True)

    def test_save_rejects_invalid_record(self):
        with self.assertRaises(ValueError):
            recorder.save_record({"notes": []}, "rossz", self.dir)
        self.assertFalse((self.dir / "rossz.json").exists())

    def test_load_rejects_bad_files(self):
        self.dir.mkdir()
        cases = {
            "nem_json": "{nem json",
            "lista": "[]",
            "format": json.dumps({**self.record, "format": "mas"}),
            "hangszer": json.dumps({**self.record, "instrument": {"name": "x", "program": 200}}),
            "hang": json.dumps({**self.record, "notes": [{"note": 60, "velocity": 0, "start": 0, "duration": 1}]}),
            "kulcs": json.dumps({**self.record, "notes": [{"note": 60}]}),
        }
        for name, text in cases.items():
            path = self.dir / f"{name}.json"
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(ValueError, msg=name):
                recorder.load_record(path)

    def test_list_records(self):
        self.assertEqual(recorder.list_records(self.dir), [])
        older = {**self.record, "created": "2026-01-01T10:00:00"}
        recorder.save_record(older, "regi", self.dir)
        recorder.save_record(self.record, "uj", self.dir)
        (self.dir / "hibas.json").write_text("{", encoding="utf-8")
        (self.dir / "jegyzet.txt").write_text("nem felvétel", encoding="utf-8")

        items = recorder.list_records(self.dir)
        self.assertEqual([i.name for i in items], ["uj", "regi", "hibas"])
        self.assertEqual(items[0].note_count, 3)
        self.assertEqual(items[0].duration, 2.0)
        self.assertEqual(items[0].instruments, ["acoustic_grand_piano"])
        self.assertIsNone(items[0].error)
        self.assertIsNotNone(items[2].error)

    def test_delete_single(self):
        a = recorder.save_record(self.record, "a", self.dir)
        b = recorder.save_record(self.record, "b", self.dir)
        self.assertEqual(recorder.delete_records([a], self.dir), 1)
        self.assertFalse(a.exists())
        self.assertTrue(b.exists())

    def test_delete_multiple(self):
        paths = [recorder.save_record(self.record, n, self.dir) for n in ("a", "b", "c")]
        self.assertEqual(recorder.delete_records(paths[:2], self.dir), 2)
        self.assertEqual([i.name for i in recorder.list_records(self.dir)], ["c"])

    def test_delete_missing_file_is_ignored(self):
        self.dir.mkdir()
        self.assertEqual(recorder.delete_records([self.dir / "nincs.json"], self.dir), 0)

    def test_delete_refuses_files_outside_records_dir(self):
        inside = recorder.save_record(self.record, "bent", self.dir)
        outside = Path(self.tmp.name) / "kint.json"
        outside.write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            recorder.delete_records([inside, outside], self.dir)
        self.assertTrue(inside.exists())
        self.assertTrue(outside.exists())


PIANO = {"name": "acoustic_grand_piano", "program": 0}
FLUTE = {"name": "flute", "program": 73}
VIOLIN = {"name": "violin", "program": 40}


def v1_record() -> dict:
    """Egy régi (1. verziójú) felvétel, ahogy a TASK-004 mentette."""
    return {
        "format": recorder.FORMAT, "version": 1, "created": "2026-10-21T19:40:12",
        "instrument": dict(VIOLIN), "duration": 1.0,
        "notes": [{"note": 60, "velocity": 100, "start": 0.0, "duration": 0.5},
                  {"note": 64, "velocity": 90, "start": 0.5, "duration": 0.5}],
    }


class VersionTwoTests(unittest.TestCase):
    """2. verzió: minden hangnak saját hangszere van; az 1. verzió továbbra is olvasható."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def mixed(self) -> dict:
        """Visszajátszott fuvola + élőben játszott zongora, a felvétel közben hegedűre váltva."""
        clock = FakeClock()
        rec = recorder.Recorder(clock=clock)
        rec.start("acoustic_grand_piano", 0)
        rec.note_on(72, 90, FLUTE)        # visszajátszott hang (saját hangszer)
        rec.note_on(72, 100)              # ugyanaz a hang a felhasználótól (zongora) — külön szól
        clock.advance(0.5)
        rec.note_off(72, FLUTE)
        rec.set_instrument("violin", 40)  # hangszerváltás lenyomott billentyűnél
        clock.advance(0.5)
        rec.note_off(72)                  # a zongorás hang zárul, nem marad lógva
        rec.note_on(76, 80)               # már hegedűvel
        clock.advance(0.5)
        return rec.stop()

    def test_new_recordings_are_version_two_with_per_note_instruments(self):
        record = self.mixed()
        self.assertEqual(record["version"], 2)
        self.assertEqual(record["instrument"], PIANO)  # az induláskori hangszer
        self.assertEqual(
            [(n["note"], n["start"], n["duration"], n["instrument"]) for n in record["notes"]],
            [(72, 0.0, 1.0, PIANO), (72, 0.0, 0.5, FLUTE), (76, 1.0, 0.5, VIOLIN)],
        )
        for n in record["notes"]:
            self.assertEqual(set(n), {"note", "velocity", "start", "duration", "instrument"})
        recorder.validate_record(record)

    def test_v2_save_load_list_delete(self):
        record = self.mixed()
        path = recorder.save_record(record, "rajatszas", self.dir)
        self.assertEqual(recorder.load_record(path), record)
        info = recorder.list_records(self.dir)[0]
        self.assertEqual(info.instruments, ["acoustic_grand_piano", "flute", "violin"])
        self.assertEqual(info.note_count, 3)
        self.assertEqual(recorder.delete_records([path], self.dir), 1)
        self.assertEqual(recorder.list_records(self.dir), [])

    def test_v1_still_loads_and_lists(self):
        path = self.dir / "regi.json"
        path.write_text(json.dumps(v1_record()), encoding="utf-8")
        self.assertEqual(recorder.load_record(path), v1_record())
        self.assertEqual(recorder.list_records(self.dir)[0].instruments, ["violin"])
        self.assertEqual(recorder.instruments_of(v1_record()), [VIOLIN])
        self.assertIsNone(recorder.note_instrument(v1_record(), v1_record()["notes"][0]))

    def test_version_specific_note_shape_is_enforced(self):
        v2_without = {**v1_record(), "version": 2}
        v1_with = {**self.mixed(), "version": 1}
        bad_instrument = self.mixed()
        bad_instrument["notes"][0]["instrument"] = {"name": "x", "program": 128}
        for name, data in {"v2 hangszer nélkül": v2_without, "v1 hangszerrel": v1_with,
                           "hibás hangszer": bad_instrument, "3. verzió": {**self.mixed(), "version": 3},
                           "bool verzió": {**v1_record(), "version": True}}.items():
            with self.assertRaises(ValueError, msg=name):
                recorder.validate_record(data)


if __name__ == "__main__":
    unittest.main()
