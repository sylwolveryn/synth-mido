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


def bars(shapes):
    return [s for s in shapes if s.kind == "bar"]


class VisualizerTests(unittest.TestCase):
    def setUp(self):
        self.v = vz.Visualizer(clock=lambda: 0.0)

    def test_idle_draws_nothing(self):
        self.assertFalse(self.v.active)
        self.assertEqual(self.v.frame(0, W, H, span), [])

    def test_note_on_spawns_bar_glow_and_sparks(self):
        self.v.note_on(60, 100, t=0.0)
        shapes = self.v.frame(0.1, W, H, span)
        kinds = [s.kind for s in shapes]
        self.assertEqual(kinds.count("bar"), 1)
        self.assertEqual(kinds.count("glow"), 1)
        self.assertEqual(kinds.count("spark"), vz.SPARKS_PER_NOTE)

    def test_bar_is_aligned_with_its_key(self):
        for note in (21, 60, 61, 108):
            v = vz.Visualizer()
            v.note_on(note, 100, t=0)
            bar = bars(v.frame(0.2, W, H, span))[0]
            k = KEYS[note]
            self.assertEqual((bar.x0, bar.x1, bar.black), (k.x0, k.x1, k.black))

    def test_sounding_bar_grows_from_the_key(self):
        self.v.note_on(60, 100, t=0)
        b1 = bars(self.v.frame(0.2, W, H, span))[0]
        b2 = bars(self.v.frame(0.5, W, H, span))[0]
        self.assertEqual(b1.y1, H)
        self.assertEqual(b2.y1, H)
        self.assertAlmostEqual(b1.y0, H - 0.2 * vz.RISE_SPEED)
        self.assertLess(b2.y0, b1.y0)

    def test_released_bar_detaches_rises_and_fades(self):
        self.v.note_on(60, 100, t=0)
        self.v.note_off(60, t=0.3)
        b = bars(self.v.frame(0.5, W, H, span))[0]
        self.assertAlmostEqual(b.y1, H - 0.2 * vz.RISE_SPEED)
        self.assertLess(b.intensity, vz._base_intensity(100))
        glows = [s for s in self.v.frame(0.5, W, H, span) if s.kind == "glow"]
        self.assertEqual(glows, [])  # csak a szóló hang ragyog

    def test_trail_is_removed_after_leaving_or_fading(self):
        self.v.note_on(60, 100, t=0)
        self.v.note_off(60, t=0.1)
        self.v.frame(5.0, W, H, span)
        self.assertFalse(self.v.active)

    def test_sounding_bar_stays_while_held(self):
        self.v.note_on(60, 100, t=0)
        self.assertEqual(len(bars(self.v.frame(30.0, W, H, span))), 1)
        self.assertTrue(self.v.active)

    def test_velocity_sets_brightness(self):
        self.v.note_on(60, 20, t=0)
        self.v.note_on(64, 127, t=0)
        b = {s.x0: s.intensity for s in bars(self.v.frame(0.1, W, H, span))}
        self.assertLess(b[KEYS[60].x0], b[KEYS[64].x0])
        self.assertAlmostEqual(b[KEYS[64].x0], 1.0)

    def test_retrigger_detaches_previous_bar(self):
        self.v.note_on(60, 100, t=0)
        self.v.note_on(60, 100, t=0.2)
        self.v.note_off(60, t=0.4)
        shapes = bars(self.v.frame(0.5, W, H, span))
        self.assertEqual(len(shapes), 2)
        self.assertTrue(all(s.y1 < H for s in shapes))

    def test_sparks_expire(self):
        self.v.note_on(60, 100, t=0)
        self.v.frame(vz.SPARK_LIFE + 0.01, W, H, span)
        self.assertEqual(self.v.sparks, [])

    def test_caps_limit_objects(self):
        for i in range(400):
            note = 21 + i % 88
            self.v.note_on(note, 100, t=i * 0.001)
            self.v.note_off(note, t=i * 0.001 + 0.0005)
        self.assertLessEqual(len(self.v.bars), vz.MAX_BARS)
        self.assertLessEqual(len(self.v.sparks), vz.MAX_SPARKS)
        shapes = self.v.frame(0.5, W, H, span)
        self.assertLessEqual(len(shapes), 2 * vz.MAX_BARS + vz.MAX_SPARKS)

    def test_caps_keep_sounding_notes_first(self):
        self.v.note_on(60, 100, t=0)  # végig szól
        for i in range(vz.MAX_BARS + 20):
            self.v.note_on(70, 100, t=0.001 * i)
            self.v.note_off(70, t=0.001 * i)
        self.assertIn(60, [b.note for b in self.v.bars])

    def test_notes_outside_keyboard_are_ignored_in_frame(self):
        self.v.note_on(12, 100, t=0)
        self.assertEqual(bars(self.v.frame(0.1, W, H, span)), [])

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

    def test_roundtrip_keeps_theme(self):
        theme.save_mode(theme.DARK_MODE, self.path)
        self.assertTrue(theme.save_setting("visual_fx", False, self.path))
        self.assertFalse(theme.load_setting("visual_fx", True, self.path))
        self.assertEqual(theme.load_mode(self.path), theme.DARK_MODE)


if __name__ == "__main__":
    unittest.main()
