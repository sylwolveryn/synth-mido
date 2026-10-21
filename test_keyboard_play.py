"""Tesztek a számítógép-billentyűzetes zongorázáshoz (ablak nélkül).

Futtatás:  python -m unittest test_keyboard_play -v
"""

import unittest

import keyboard_play as kp
from test_playback import FakeTimer

US_ORDER = ["a", "w", "s", "e", "d", "f", "t", "g", "y", "h", "u", "j", "k", "o", "l", "p", "semicolon", "apostrophe"]
HU_ORDER = ["a", "w", "s", "e", "d", "f", "t", "g", "z", "h", "u", "j", "k", "o", "l", "p", "eacute", "aacute"]


class MappingTests(unittest.TestCase):
    def test_us_qwerty_plays_chromatic_c4_to_f5(self):
        self.assertEqual([kp.note_for(k) for k in US_ORDER], list(range(60, 78)))

    def test_hungarian_qwertz_plays_chromatic_c4_to_f5(self):
        self.assertEqual([kp.note_for(k) for k in HU_ORDER], list(range(60, 78)))

    def test_keysym_as_character(self):
        # egyes Tk verziók a karaktert adják keysym-ként
        self.assertEqual([kp.note_for(k) for k in ("é", "É", "á", ";", "'")], [76, 76, 77, 76, 77])

    def test_at_least_one_and_a_half_octaves(self):
        notes = {kp.note_for(k) for k in kp.KEYMAP}
        self.assertGreaterEqual(len(notes), 18)

    def test_white_keys_on_home_row_black_keys_above(self):
        white = ["a", "s", "d", "f", "g", "h", "j", "k", "l", "semicolon", "apostrophe"]
        black = ["w", "e", "t", "y", "u", "o", "p"]
        self.assertEqual([kp.note_for(k) % 12 in {1, 3, 6, 8, 10} for k in white], [False] * len(white))
        self.assertEqual([kp.note_for(k) % 12 in {1, 3, 6, 8, 10} for k in black], [True] * len(black))

    def test_case_insensitive_and_unknown(self):
        self.assertEqual(kp.note_for("A"), 60)
        self.assertEqual(kp.note_for("Eacute"), 76)
        self.assertIsNone(kp.note_for("q"))
        self.assertIsNone(kp.note_for("Return"))

    def test_base_and_range_clipping(self):
        self.assertEqual(kp.note_for("a", base=48), 48)
        self.assertIsNone(kp.note_for("apostrophe", base=96))  # 113 > C8
        self.assertEqual(kp.note_for("k", base=96), 108)
        self.assertIsNone(kp.note_for("a", base=12))


class KeyboardPlayerTests(unittest.TestCase):
    def setUp(self):
        self.timer = FakeTimer()
        self.log = []
        self.kb = kp.KeyboardPlayer(self.timer.after, self.timer.cancel, lambda n, on: self.log.append((n, on)))

    def test_press_and_release(self):
        self.assertTrue(self.kb.press("a"))
        self.assertEqual(self.log, [(60, True)])
        self.assertTrue(self.kb.release("a"))
        self.assertEqual(self.log, [(60, True)])  # késleltetett elengedés
        self.timer.advance(0.05)
        self.assertEqual(self.log, [(60, True), (60, False)])

    def test_windows_autorepeat_does_not_retrigger(self):
        for _ in range(5):
            self.kb.press("a")
        self.kb.release("a")
        self.timer.advance(0.05)
        self.assertEqual(self.log, [(60, True), (60, False)])

    def test_x11_autorepeat_does_not_retrigger(self):
        self.kb.press("a")
        for _ in range(5):
            self.kb.release("a")
            self.kb.press("a")  # azonnal, a késleltetésen belül
        self.timer.advance(0.05)
        self.assertEqual(self.log, [(60, True)])
        self.kb.release("a")
        self.timer.advance(0.05)
        self.assertEqual(self.log, [(60, True), (60, False)])

    def test_real_repeat_after_release_retriggers(self):
        self.kb.press("a")
        self.kb.release("a")
        self.timer.advance(0.05)
        self.kb.press("a")
        self.assertEqual(self.log, [(60, True), (60, False), (60, True)])

    def test_chord(self):
        for k in ("a", "d", "g"):
            self.kb.press(k)
        self.assertEqual(self.kb.sounding, {60, 64, 67})
        for k in ("a", "d", "g"):
            self.kb.release(k)
        self.timer.advance(0.05)
        self.assertEqual(self.kb.sounding, set())
        self.assertEqual(sorted(n for n, on in self.log if not on), [60, 64, 67])

    def test_non_piano_keys_are_not_handled(self):
        self.assertFalse(self.kb.press("q"))
        self.assertFalse(self.kb.release("Return"))
        self.assertEqual(self.log, [])

    def test_release_uses_note_from_press_time(self):
        self.kb.press("a")
        self.kb.base = 72
        self.kb.release("a")
        self.timer.advance(0.05)
        self.assertEqual(self.log, [(60, True), (60, False)])

    def test_out_of_range_key_is_silent(self):
        self.kb.base = 96
        self.assertTrue(self.kb.press("apostrophe"))
        self.kb.release("apostrophe")
        self.timer.advance(0.05)
        self.assertEqual(self.log, [])

    def test_release_all(self):
        self.kb.press("a")
        self.kb.press("s")
        self.kb.release("s")  # függő elengedés is
        self.kb.release_all()
        self.assertEqual(sorted(self.log), [(60, False), (60, True), (62, False), (62, True)])
        self.assertEqual(self.kb.held, {})
        self.timer.advance(0.1)
        self.assertEqual(len(self.log), 4)


class OctaveShiftTests(unittest.TestCase):
    def setUp(self):
        self.timer = FakeTimer()
        self.log = []
        self.changes = 0
        self.kb = kp.KeyboardPlayer(
            self.timer.after, self.timer.cancel, lambda n, on: self.log.append((n, on)),
            on_range_change=self._changed,
        )

    def _changed(self):
        self.changes += 1

    def test_default_range_is_c4_to_f5(self):
        self.assertEqual(self.kb.range_notes(), (60, 77))

    def test_x_down_c_up(self):
        self.kb.press("x")
        self.kb.release("x")
        self.assertEqual(self.kb.base, 48)
        self.kb.press("C")
        self.kb.release("C")
        self.kb.press("c")
        self.assertEqual(self.kb.base, 72)
        self.assertEqual(self.changes, 3)
        self.assertEqual(self.log, [])  # az oktáv gombok nem szólnak

    def test_holding_octave_key_does_not_repeat(self):
        for _ in range(5):
            self.kb.press("c")
        self.assertEqual(self.kb.base, 72)
        self.kb.release("c")
        self.kb.press("c")
        self.assertEqual(self.kb.base, 84)

    def test_notes_follow_the_shift(self):
        self.kb.shift(-2)
        self.kb.press("a")
        self.assertEqual(self.log, [(36, True)])

    def test_limits_reach_a0_and_c8(self):
        while self.kb.shift(-1):
            pass
        self.assertEqual(self.kb.base, kp.MIN_BASE)
        self.assertEqual(self.kb.range_notes(), (21, 29))
        self.kb.press("h")  # A0
        self.kb.press("a")  # C0 — tartományon kívül, néma
        self.assertEqual(self.log, [(21, True)])
        self.kb.release_all()
        self.log.clear()
        while self.kb.shift(1):
            pass
        self.assertEqual(self.kb.base, kp.MAX_BASE)
        self.assertEqual(self.kb.range_notes(), (96, 108))
        self.kb.press("k")  # C8
        self.kb.press("o")  # C#8 — néma
        self.assertEqual(self.log, [(108, True)])
        self.assertFalse(self.kb.shift(1))

    def test_shift_while_held_releases_original_note(self):
        self.kb.press("a")
        self.kb.press("c")
        self.kb.release("a")
        self.timer.advance(0.05)
        self.assertEqual(self.log, [(60, True), (60, False)])
        self.assertEqual(self.kb.sounding, set())

    def test_labels_follow_range(self):
        labels = self.kb.key_labels()
        self.assertEqual(labels[60], "A")
        self.assertEqual(labels[68], "Z")
        self.assertEqual(labels[77], "Á")
        self.assertEqual(len(labels), 18)
        self.kb.base = kp.MAX_BASE
        self.assertEqual(max(self.kb.key_labels()), 108)
        self.assertEqual(self.kb.key_labels()[108], "K")


if __name__ == "__main__":
    unittest.main()
