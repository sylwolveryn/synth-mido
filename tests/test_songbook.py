"""Tesztek a daloskönyvhöz: jelölés, érvényes felvételek, tartomány, hossz, nevek, szólamok igazítása.

Futtatás:  python -m unittest tests.test_songbook -v
"""

import tempfile
import unittest
from pathlib import Path

from synth_mido.config import INSTRUMENTS
from synth_mido.core import recorder, songbook as sb
from synth_mido.core.piano_layout import FIRST_NOTE, LAST_NOTE
from synth_mido.core.playback import build_schedule

# modern, szerzői jogvédett művek — nem lehetnek a daloskönyvben
COPYRIGHTED = ("imperial march", "star wars", "harry potter", "pirates of the caribbean", "despacito")


class NotationTests(unittest.TestCase):
    def test_parse_pitch(self):
        self.assertEqual(sb.parse_pitch("C4"), 60)
        self.assertEqual(sb.parse_pitch("A4"), 69)
        self.assertEqual(sb.parse_pitch("F#4"), 66)
        self.assertEqual(sb.parse_pitch("Bb3"), 58)
        self.assertEqual(sb.parse_pitch("E#4"), 65)
        self.assertEqual(sb.parse_pitch("B#3"), 60)
        self.assertEqual(sb.parse_pitch("A0"), 21)
        self.assertEqual(sb.parse_pitch("C8"), 108)

    def test_parse_voice(self):
        self.assertEqual(sb.parse_voice("E5:.5 | R:1 C4+E4:2 G4"),
                         [((76,), 0.5), ((), 1.0), ((60, 64), 2.0), ((67,), 1.0)])
        self.assertEqual(sb.voice_beats("C4:2 R:.5 D4:.25"), 2.75)

    def test_to_record_timing(self):
        song = sb.Song("t", "x", "1800", "acoustic_grand_piano",
                       [sb.Section(120, [(90, "C4 D4:2"), (60, "C3:3")]), sb.Section(60, [(90, "E4")])])
        rec = song.to_record()
        starts = [(n["note"], n["start"]) for n in rec["notes"]]
        self.assertEqual(starts, [(48, 0.0), (60, 0.0), (62, 0.5), (64, 1.5)])
        self.assertEqual(rec["duration"], 2.5)
        self.assertAlmostEqual(rec["notes"][1]["duration"], 0.5 * sb.LEGATO)


class SongbookTests(unittest.TestCase):
    def test_at_least_15_songs_with_unique_names(self):
        self.assertGreaterEqual(len(sb.SONGS), 15)
        names = [s.name for s in sb.SONGS]
        self.assertEqual(len(names), len(set(names)))
        for wanted in ("Für Elise", "Ode to Joy", "Rondo alla Turca", "In the Hall of the Mountain King",
                       "Canon in D", "Funeral March"):
            self.assertIn(wanted, names)

    def test_no_copyrighted_works(self):
        for song in sb.SONGS:
            self.assertFalse(any(c in song.name.lower() for c in COPYRIGHTED), song.name)
            self.assertLess(int(song.year), 1930, song.name)  # régi, közkincs művek

    def test_names_are_valid_file_names(self):
        for song in sb.SONGS:
            self.assertEqual(recorder.sanitize_name(song.name), song.name)

    def test_every_song_is_a_valid_record(self):
        for song in sb.SONGS:
            with self.subTest(song=song.name):
                rec = song.to_record()
                recorder.validate_record(rec)
                self.assertIn(song.instrument, INSTRUMENTS)
                notes = [n["note"] for n in rec["notes"]]
                self.assertTrue(all(FIRST_NOTE <= n <= LAST_NOTE for n in notes))
                self.assertGreaterEqual(len(notes), 30)
                self.assertTrue(5 <= rec["duration"] <= 120, rec["duration"])
                self.assertTrue(all(n["start"] + n["duration"] <= rec["duration"] + 0.01 for n in rec["notes"]))
                self.assertTrue(build_schedule(rec))

    def test_voices_in_each_section_are_aligned(self):
        for song in sb.SONGS:
            for i, section in enumerate(song.sections):
                lengths = {round(sb.voice_beats(tokens), 2) for _, tokens in section.voices}
                self.assertEqual(len(lengths), 1, f"{song.name} szakasz {i}: {lengths}")

    def test_write_all_creates_loadable_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = sb.write_all(Path(tmp))
            self.assertEqual(len(paths), len(sb.SONGS))
            self.assertEqual({p.stem for p in paths}, {s.name for s in sb.SONGS})
            for p in paths:
                self.assertEqual(recorder.load_record(p), sb.SONGS[[s.name for s in sb.SONGS].index(p.stem)].to_record())
            # újragenerálás felülír, nem dob hibát
            self.assertEqual(len(sb.write_all(Path(tmp))), len(sb.SONGS))


if __name__ == "__main__":
    unittest.main()
