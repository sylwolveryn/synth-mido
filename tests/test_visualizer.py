"""Tesztek a hangvizualizáció modelljéhez és a beállítás mentéshez (ablak nélkül).

Futtatás:  python -m unittest test_visualizer -v
"""

import tempfile
import unittest
from pathlib import Path

from synth_mido.core import piano_layout
from synth_mido.fx import visualizer as vz
from synth_mido.skins import theme

H = 100.0
W = 1040.0
KEYS = {k.note: k for k in piano_layout.layout(W, 150)}


def span(note):
    k = KEYS.get(note)
    return (k.x0, k.x1, k.black) if k else None


def of(kind, shapes):
    return [s for s in shapes if s.kind == kind]


def xs(shape):
    return shape.points[0::2]


def ys(shape):
    return shape.points[1::2]


class FlameTests(unittest.TestCase):
    def setUp(self):
        self.v = vz.Visualizer(clock=lambda: 0.0)

    def test_idle_draws_nothing(self):
        self.assertFalse(self.v.active)
        self.assertEqual(self.v.frame(0, W, H, span), [])

    def test_note_on_lights_a_glowing_flame_with_embers(self):
        self.v.note_on(60, 100, t=0.0)
        kinds = [s.kind for s in self.v.frame(0.1, W, H, span)]
        self.assertEqual(kinds.count("halo"), len(vz.HALO_WIDTH))   # többrétegű fényudvar
        self.assertEqual(kinds.count("flame"), 1)
        self.assertEqual(kinds.count("core"), 1)
        self.assertEqual(kinds.count("ember"), vz.EMBER_BURST)

    def test_layers_are_drawn_back_to_front(self):
        for note in (60, 64, 67):
            self.v.note_on(note, 100, t=0)
        kinds = [s.kind for s in self.v.frame(0.2, W, H, span)]
        order = {k: i for i, k in enumerate(("halo", "ember", "flame", "core"))}
        self.assertEqual([order[k] for k in kinds], sorted(order[k] for k in kinds))

    def test_flame_stands_on_its_key(self):
        for note in (21, 60, 61, 108):
            v = vz.Visualizer()
            v.note_on(note, 100, t=0)
            flame = of("flame", v.frame(0.2, W, H, span))[0]
            k = KEYS[note]
            self.assertEqual(max(ys(flame)), H)                    # a sáv aljáról, a billentyűből nő ki
            base = [x for x, y in zip(xs(flame), ys(flame)) if y == H]
            self.assertAlmostEqual(sum(base) / 2, (k.x0 + k.x1) / 2)  # a billentyű közepén áll
            self.assertTrue(flame.black == k.black)

    def test_flame_flares_up_then_flickers(self):
        self.v.note_on(60, 100, t=0)
        heights = [H - min(ys(of("flame", self.v.frame(t, W, H, span))[0])) for t in (0.02, 0.2, 0.33, 0.47)]
        self.assertLess(heights[0], heights[1])                 # felcsap
        self.assertGreater(len({round(h, 1) for h in heights[1:]}), 1)  # lobog
        self.assertTrue(all(h <= H for h in heights))

    def test_core_is_inside_the_flame(self):
        self.v.note_on(60, 100, t=0)
        shapes = self.v.frame(0.3, W, H, span)
        flame, core = of("flame", shapes)[0], of("core", shapes)[0]
        self.assertGreater(min(ys(core)), min(ys(flame)))
        self.assertLess(max(xs(core)) - min(xs(core)), max(xs(flame)) - min(xs(flame)))

    def test_velocity_sets_height_and_brightness(self):
        self.v.note_on(60, 20, t=0)
        self.v.note_on(72, 127, t=0)
        flames = {round(sum(xs(f)) / len(xs(f)) // 30): f for f in of("flame", self.v.frame(0.2, W, H, span))}
        quiet, loud = sorted(flames.values(), key=lambda f: f.intensity)
        self.assertLess(H - min(ys(quiet)), H - min(ys(loud)))
        self.assertAlmostEqual(loud.intensity, 1.0)

    def test_held_note_keeps_burning_and_sheds_embers(self):
        self.v.note_on(60, 100, t=0)
        for i in range(1, 61):                     # 2 mp, ~30 fps
            shapes = self.v.frame(i / 30, W, H, span)
        self.assertEqual(len(of("flame", shapes)), 1)
        self.assertGreater(len(of("ember", shapes)), 0)   # a gyújtási parázs rég kialudt, ezek újak
        self.assertTrue(self.v.active)

    def test_release_dies_down_and_goes_out(self):
        self.v.note_on(60, 100, t=0)
        self.v.frame(0.3, W, H, span)
        self.v.note_off(60, t=0.3)
        before = of("flame", self.v.frame(0.31, W, H, span))[0]
        after = of("flame", self.v.frame(0.3 + vz.FADE * 0.7, W, H, span))[0]
        self.assertLess(after.intensity, before.intensity)
        self.assertLess(H - min(ys(after)), H - min(ys(before)))
        self.v.frame(0.3 + vz.FADE + vz.EMBER_LIFE + 0.1, W, H, span)
        self.assertFalse(self.v.active)

    def test_retrigger_lights_a_new_flame(self):
        self.v.note_on(60, 100, t=0)
        self.v.note_on(60, 100, t=0.2)
        self.assertEqual(len(of("flame", self.v.frame(0.25, W, H, span))), 2)
        self.v.frame(0.2 + vz.FADE + 0.05, W, H, span)
        self.assertEqual(len(self.v.flames), 1)

    def test_embers_rise_and_expire(self):
        self.v.note_on(60, 100, t=0)
        e1 = of("ember", self.v.frame(0.1, W, H, span))
        e2 = of("ember", self.v.frame(0.3, W, H, span))
        self.assertLess(sum(ys(e2[0])), sum(ys(e1[0])))
        self.v.note_off(60, t=0.3)
        self.v.frame(0.3 + vz.EMBER_LIFE + 0.05, W, H, span)
        self.assertEqual(self.v.embers, [])

    def test_caps_limit_objects(self):
        for i in range(400):
            note = 21 + i % 88
            self.v.note_on(note, 100, t=i * 0.001)
            if i % 3:
                self.v.note_off(note, t=i * 0.001 + 0.0005)
        self.assertLessEqual(len(self.v.flames), vz.MAX_FLAMES)
        self.assertLessEqual(len(self.v.embers), vz.MAX_EMBERS)
        shapes = self.v.frame(0.45, W, H, span)
        self.assertLessEqual(len(shapes), (len(vz.HALO_WIDTH) + 2) * vz.MAX_FLAMES + vz.MAX_EMBERS)

    def test_caps_keep_sounding_notes_first(self):
        self.v.note_on(60, 100, t=0)  # végig szól
        for i in range(vz.MAX_FLAMES + 20):
            self.v.note_on(70, 100, t=0.001 * i)
            self.v.note_off(70, t=0.001 * i)
        self.assertIn(60, [f.note for f in self.v.flames])

    def test_notes_outside_keyboard_are_ignored_in_frame(self):
        self.v.note_on(12, 100, t=0)
        self.assertEqual(self.v.frame(0.1, W, H, span), [])

    def test_clear(self):
        self.v.note_on(60, 100, t=0)
        self.v.clear()
        self.assertFalse(self.v.active)


class SettingsHelperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "s" / "settings.json"

    def test_default_when_missing(self):
        self.assertTrue(theme.load_setting("visual_fx", True, self.path))

    def test_roundtrip_keeps_skin(self):
        theme.save_skin("forest", theme.LIGHT, self.path)
        self.assertTrue(theme.save_setting("visual_fx", False, self.path))
        self.assertFalse(theme.load_setting("visual_fx", True, self.path))
        self.assertEqual(theme.load_skin(self.path), ("forest", theme.LIGHT))


if __name__ == "__main__":
    unittest.main()
