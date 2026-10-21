"""Tesztek a 88 billentyűs zongora geometriájához (ablak nélkül).

Futtatás:  python -m unittest test_piano_layout -v
"""

import unittest

import piano_layout as pl


class RangeTests(unittest.TestCase):
    def test_88_keys_52_white_36_black(self):
        keys = pl.layout(1040, 150)
        self.assertEqual(len(keys), 88)
        self.assertEqual(sum(not k.black for k in keys), 52)
        self.assertEqual(sum(k.black for k in keys), 36)
        self.assertEqual(sorted(k.note for k in keys), list(range(21, 109)))

    def test_range_ends(self):
        self.assertEqual(pl.note_label(pl.FIRST_NOTE), "A0")
        self.assertEqual(pl.note_label(pl.LAST_NOTE), "C8")
        self.assertEqual(pl.note_label(pl.MIDDLE_C), "C4")
        self.assertEqual([pl.is_black(n) for n in (21, 22, 23, 24)], [False, True, False, False])
        self.assertFalse(pl.is_black(108))

    def test_octave_pattern(self):
        self.assertEqual([pl.is_black(n) for n in range(60, 72)],
                         [False, True, False, True, False, False, True, False, True, False, True, False])

    def test_labels_are_the_c_keys(self):
        self.assertEqual([pl.note_label(n) for n in pl.label_notes()], [f"C{i}" for i in range(1, 9)])


class GeometryTests(unittest.TestCase):
    def setUp(self):
        self.width, self.height = 780.0, 150.0
        self.keys = pl.layout(self.width, self.height)
        self.by_note = {k.note: k for k in self.keys}

    def test_white_keys_fill_width_without_gaps(self):
        whites = [k for k in self.keys if not k.black]
        self.assertAlmostEqual(whites[0].x0, 0.0)
        self.assertAlmostEqual(whites[-1].x1, self.width)
        for a, b in zip(whites, whites[1:]):
            self.assertAlmostEqual(a.x1, b.x0)
            self.assertAlmostEqual(a.x1 - a.x0, self.width / 52)
            self.assertEqual(a.y1, self.height)

    def test_black_keys_sit_between_neighbours(self):
        for k in self.keys:
            if not k.black:
                continue
            left, right = self.by_note[k.note - 1], self.by_note[k.note + 1]
            center = (k.x0 + k.x1) / 2
            self.assertAlmostEqual(center, left.x1)
            self.assertAlmostEqual(center, right.x0)
            self.assertLess(k.y1, self.height)

    def test_whites_are_drawn_before_blacks(self):
        flags = [k.black for k in self.keys]
        self.assertEqual(flags, sorted(flags))

    def test_key_at_prefers_black_keys(self):
        cs4 = self.by_note[61]
        c4 = self.by_note[60]
        top_y, bottom_y = 5, self.height - 5
        center = (cs4.x0 + cs4.x1) / 2
        self.assertEqual(pl.key_at(self.keys, center, top_y), 61)
        # a fekete billentyű alatt a fehérek: a határtól balra C4, jobbra D4
        self.assertEqual(pl.key_at(self.keys, center - 1, bottom_y), 60)
        self.assertEqual(pl.key_at(self.keys, center + 1, bottom_y), 62)
        self.assertEqual(pl.key_at(self.keys, c4.x0 + 1, bottom_y), 60)

    def test_key_at_range_ends_and_outside(self):
        self.assertEqual(pl.key_at(self.keys, 1, self.height - 1), 21)
        self.assertEqual(pl.key_at(self.keys, self.width - 1, self.height - 1), 108)
        self.assertIsNone(pl.key_at(self.keys, self.width + 5, 10))
        self.assertIsNone(pl.key_at(self.keys, 10, self.height + 5))

    def test_rescales_with_width(self):
        wide = pl.layout(self.width * 2, self.height)
        for a, b in zip(self.keys, wide):
            self.assertEqual(a.note, b.note)
            self.assertAlmostEqual(b.x0, a.x0 * 2)
            self.assertAlmostEqual(b.x1, a.x1 * 2)

    def test_every_key_clickable_at_minimum_width(self):
        keys = pl.layout(740, 150)
        for k in keys:
            y = k.y1 - 2 if not k.black else k.y0 + 2
            x = (k.x0 + k.x1) / 2
            self.assertEqual(pl.key_at(keys, x, y), k.note, pl.note_label(k.note))


if __name__ == "__main__":
    unittest.main()
