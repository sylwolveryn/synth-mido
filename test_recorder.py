"""Tesztek a recorder modulhoz: felvétel szerkezete, mentés, betöltés, listázás, törlés.

Futtatás:  python -m unittest test_recorder -v
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import recorder


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
        self.assertEqual(self.record["notes"], [
            {"note": 60, "velocity": 100, "start": 0.0, "duration": 0.75},
            {"note": 64, "velocity": 80, "start": 0.5, "duration": 0.5},
            {"note": 67, "velocity": 90, "start": 1.0, "duration": 1.0},
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
        self.assertEqual(items[0].instrument, "acoustic_grand_piano")
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


if __name__ == "__main__":
    unittest.main()
