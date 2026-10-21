"""Tesztek az oktáv duplázáshoz (ablak nélkül).

Futtatás:  python -m unittest test_doubling -v
"""

import unittest

from synth_mido.core import doubling as d


class TargetTests(unittest.TestCase):
    def test_directions(self):
        self.assertEqual(d.targets(60, d.OFF), [60])
        self.assertEqual(d.targets(60, d.UP), [60, 72])
        self.assertEqual(d.targets(60, d.DOWN), [60, 48])
        self.assertEqual(d.targets(60, d.BOTH), [60, 48, 72])

    def test_range_edges_are_skipped(self):
        self.assertEqual(d.targets(21, d.DOWN), [21])          # A0 alatt nincs billentyű
        self.assertEqual(d.targets(100, d.UP), [100])          # 112 > C8
        self.assertEqual(d.targets(30, d.BOTH), [30, 42])
        self.assertEqual(d.targets(96, d.BOTH), [96, 84, 108])

    def test_labels_and_default(self):
        self.assertEqual(d.DEFAULT_MODE, d.OFF)
        self.assertEqual([d.label(m) for m in d.MODES], ["Ki", "+1 oktáv", "−1 oktáv", "±1 oktáv"])


class DoublerTests(unittest.TestCase):
    def test_press_and_release(self):
        x = d.OctaveDoubler(d.UP)
        self.assertEqual(x.press(60), [60, 72])
        self.assertEqual(x.sounding, {60, 72})
        self.assertEqual(sorted(x.release(60)), [60, 72])
        self.assertEqual(x.sounding, set())

    def test_shared_note_keeps_sounding_while_needed(self):
        x = d.OctaveDoubler(d.UP)
        x.press(60)                     # C4 + C5
        self.assertEqual(x.press(72), [72, 84])   # C5 újra megszólal + C6
        self.assertEqual(x.release(60), [60])     # C5-öt még a C5 billentyű kéri
        self.assertEqual(sorted(x.release(72)), [72, 84])
        self.assertEqual(x.sounding, set())

    def test_mode_change_while_held_releases_what_was_started(self):
        x = d.OctaveDoubler(d.BOTH)
        x.press(60)
        x.set_mode(d.OFF)
        self.assertEqual(sorted(x.release(60)), [48, 60, 72])
        x.press(60)
        x.set_mode(d.UP)
        self.assertEqual(x.release(60), [60])

    def test_repeated_press_of_held_key_is_ignored(self):
        x = d.OctaveDoubler(d.UP)
        x.press(60)
        self.assertEqual(x.press(60), [])
        self.assertEqual(sorted(x.release(60)), [60, 72])
        self.assertEqual(x.release(60), [])

    def test_off_mode_is_plain(self):
        x = d.OctaveDoubler()
        self.assertEqual(x.press(64), [64])
        self.assertEqual(x.release(64), [64])

    def test_invalid_mode_ignored(self):
        x = d.OctaveDoubler("sideways")
        self.assertEqual(x.mode, d.OFF)
        x.set_mode("sideways")
        self.assertEqual(x.mode, d.OFF)


class MultiOctaveTests(unittest.TestCase):
    def test_targets_with_extra_offsets_dedup_and_range(self):
        self.assertEqual(d.targets(60, d.OFF, (-24, 12)), [60, 36, 72])
        self.assertEqual(d.targets(60, d.UP, (12, 24)), [60, 72, 84])       # a +12 csak egyszer
        self.assertEqual(d.targets(100, d.OFF, (12, -12)), [100, 88])       # 112 > C8 kimarad

    def test_selection_default_is_only_the_keyboard_octave(self):
        sel = d.OctaveSelection(60)
        self.assertEqual(sel.selected(), [60])
        self.assertEqual(sel.offsets(), ())
        self.assertEqual(sel.label(), "C4")
        self.assertEqual(len(d.OCTAVE_BASES), 8)
        self.assertEqual([d.octave_label(o) for o in (12, 96)], ["C0", "C7"])

    def test_toggle_extras_and_offsets(self):
        sel = d.OctaveSelection(60)
        self.assertTrue(sel.toggle(36))
        self.assertTrue(sel.toggle(84))
        self.assertEqual(sel.selected(), [36, 60, 84])
        self.assertEqual(sel.offsets(), (-24, 24))
        self.assertEqual(sel.label(), "C2 · C4 · C6")
        self.assertTrue(sel.toggle(36))
        self.assertEqual(sel.offsets(), (24,))

    def test_keyboard_octave_cannot_be_unticked_and_follows_base(self):
        sel = d.OctaveSelection(60)
        self.assertFalse(sel.toggle(60))
        self.assertFalse(sel.toggle(61))
        sel.toggle(84)
        sel.set_base(72)                      # X / C eltolás
        self.assertEqual(sel.selected(), [72, 84])
        self.assertEqual(sel.offsets(), (12,))
        sel.set_base(84)                      # a bejelölt oktávra lép: nincs dupla hang
        self.assertEqual(sel.offsets(), ())
        self.assertTrue(sel.is_selected(84))

    def test_doubler_uses_extra_offsets_and_releases_what_it_started(self):
        x = d.OctaveDoubler(d.OFF)
        x.set_extra_offsets((-12, 12))
        self.assertEqual(x.press(60), [60, 48, 72])
        x.set_extra_offsets(())               # váltás lenyomva
        self.assertEqual(sorted(x.release(60)), [48, 60, 72])
        self.assertEqual(x.sounding, set())


if __name__ == "__main__":
    unittest.main()
