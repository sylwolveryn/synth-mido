"""Tesztek a hangszer illusztrációkhoz: minden hangszerhez van rajz, és a rajz a dobozában marad.

Futtatás:  python -m unittest tests.test_instrument_art -v
"""

import unittest

from synth_mido import config
from synth_mido.core import i18n
from synth_mido.fx import instrument_art as art
from synth_mido.skins import registry
from tests.test_skins import FakeCanvas


class MappingTests(unittest.TestCase):
    def test_sixteen_families_with_distinct_animals_and_instruments(self):
        self.assertEqual(len(art.FAMILIES), 16)
        self.assertEqual(len({f.animal for f in art.FAMILIES}), 16)
        self.assertEqual(len({f.instrument for f in art.FAMILIES}), 16)

    def test_every_general_midi_instrument_has_an_illustration(self):
        for name, program in config.INSTRUMENTS.items():
            family = art.family_of(program)
            self.assertIn(family.animal, art.ANIMALS, name)
            self.assertIn(family.instrument, art.INSTRUMENTS, name)
            self.assertIn(f"art.{family.id}", i18n.load_file(i18n.REFERENCE), name)

    def test_known_examples(self):
        by_name = {name: art.family_of(program) for name, program in config.INSTRUMENTS.items()}
        self.assertEqual((by_name["flute"].animal, by_name["flute"].instrument), ("bird", "flute"))
        self.assertEqual(by_name["acoustic_grand_piano"].instrument, "piano")
        self.assertEqual(by_name["violin"].instrument, "violin")
        self.assertEqual(by_name["trumpet"].animal, "elephant")

    def test_out_of_range_falls_back_to_piano(self):
        self.assertEqual(art.family_of(-1).id, "piano")
        self.assertEqual(art.family_of(500).id, "piano")


class PaintTests(unittest.TestCase):
    def test_every_scene_draws_inside_its_box_in_every_skin(self):
        x, y, size = 30, 5, 84
        for skin in registry.all_skins():
            for scheme in ("dark", "light"):
                palette = skin.palette(scheme)
                for family_index in range(16):
                    canvas = FakeCanvas()
                    family = art.paint(canvas, family_index * 8, x, y, size, palette)
                    self.assertEqual(family, art.FAMILIES[family_index])
                    self.assertGreater(len(canvas.calls), 15, family.id)
                    for _, coords, kwargs in canvas.calls:
                        xs, ys = coords[0::2], coords[1::2]
                        self.assertTrue(all(x - 1 <= v <= x + size + 1 for v in xs), (skin.id, family.id, coords))
                        self.assertTrue(all(y - 1 <= v <= y + size * 1.05 for v in ys), (skin.id, family.id, coords))
                        self.assertEqual(kwargs.get("tags"), ("art",))

    def test_scales_with_size(self):
        small, big = FakeCanvas(), FakeCanvas()
        palette = registry.all_skins()[0].palette("dark")
        art.paint(small, 73, 0, 0, 50, palette)
        art.paint(big, 73, 0, 0, 100, palette)
        self.assertEqual(len(small.calls), len(big.calls))
        self.assertAlmostEqual(max(max(c[1]) for c in big.calls), 2 * max(max(c[1]) for c in small.calls), delta=1)

    def test_colours_follow_the_skin(self):
        fills = {}
        for skin_id in ("synthwave", "classic"):
            canvas = FakeCanvas()
            art.paint(canvas, 0, 0, 0, 84, [s for s in registry.all_skins() if s.id == skin_id][0].palette("dark"))
            fills[skin_id] = {kw.get("fill") for _, _, kw in canvas.calls}
        self.assertNotEqual(fills["synthwave"], fills["classic"])


if __name__ == "__main__":
    unittest.main()
