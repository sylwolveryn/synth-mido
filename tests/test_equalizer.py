"""Tesztek a hangszínszabályzó spektrum modelljéhez és az animációkhoz (ablak nélkül).

Futtatás:  python -m unittest tests.test_equalizer -v
"""

import unittest

from synth_mido.fx import animations, spectrum
from synth_mido.fx.spectrum import Spectrum, band_of


class Clock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def run(s, clock, seconds, fps=30):
    for _ in range(int(seconds * fps)):
        clock.t += 1 / fps
        s.step()


class SpectrumTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.s = Spectrum(clock=self.clock)

    def test_band_mapping(self):
        self.assertEqual(band_of(21), 0)
        self.assertEqual(band_of(108), spectrum.BANDS - 1)
        bands = [band_of(n) for n in range(21, 109)]
        self.assertEqual(bands, sorted(bands))
        self.assertEqual(len(set(bands)), spectrum.BANDS)
        self.assertEqual(band_of(5), 0)

    def test_silent_spectrum(self):
        run(self.s, self.clock, 0.5)
        self.assertEqual(max(self.s.levels), 0.0)
        self.assertFalse(self.s.active)
        self.assertEqual(self.s.wave(16), [0.0] * 16)

    def test_note_raises_its_band_and_neighbours(self):
        self.s.note_on(60, 127)
        run(self.s, self.clock, 0.2)
        b = band_of(60)
        self.assertGreater(self.s.levels[b], 0.7)
        self.assertGreater(self.s.levels[b + 1], 0.2)
        self.assertGreater(self.s.levels[band_of(72)], 0.15)    # felhang
        self.assertLess(self.s.levels[0], 0.01)

    def test_velocity_scales_level(self):
        quiet = Spectrum(clock=self.clock)
        self.s.note_on(60, 127)
        quiet.note_on(60, 30)
        for _ in range(6):
            self.clock.t += 1 / 30
            self.s.step()
            quiet.step()
        self.assertGreater(self.s.levels[band_of(60)], quiet.levels[band_of(60)] * 2)

    def test_held_note_sustains_released_note_decays(self):
        self.s.note_on(60, 120)
        run(self.s, self.clock, 2.0)
        held = self.s.levels[band_of(60)]
        self.assertGreater(held, 0.6)
        self.s.note_off(60)
        run(self.s, self.clock, 0.2)
        self.assertLess(self.s.levels[band_of(60)], held)
        run(self.s, self.clock, 2.0)
        self.assertLess(self.s.levels[band_of(60)], 0.01)

    def test_peak_holds_then_falls(self):
        self.s.note_on(60, 127)
        run(self.s, self.clock, 0.2)
        self.s.note_off(60)
        b = band_of(60)
        peak = self.s.peaks[b]
        run(self.s, self.clock, spectrum.PEAK_HOLD * 0.6)
        self.assertAlmostEqual(self.s.peaks[b], peak, places=3)
        self.assertGreater(self.s.peaks[b], self.s.levels[b])
        run(self.s, self.clock, 2.5)
        self.assertLess(self.s.peaks[b], 0.05)

    def test_large_time_gap_is_clamped(self):
        self.s.note_on(60, 127)
        self.clock.t += 10
        self.s.step()
        self.assertLessEqual(max(self.s.levels), 1.0)

    def test_wave_bounds(self):
        for n in (40, 60, 64, 67):
            self.s.note_on(n, 110)
        run(self.s, self.clock, 0.3)
        wave = self.s.wave(200)
        self.assertEqual(len(wave), 200)
        self.assertTrue(all(-1.0 <= v <= 1.0 for v in wave))
        self.assertGreater(max(abs(v) for v in wave), 0.1)

    def test_clear(self):
        self.s.note_on(60)
        run(self.s, self.clock, 0.2)
        self.s.clear()
        self.assertFalse(self.s.active)


class AnimationTests(unittest.TestCase):
    def loud_spectrum(self):
        clock = Clock()
        s = Spectrum(clock=clock)
        for n in (28, 45, 60, 64, 67, 79, 96, 108):
            s.note_on(n, 120)
        run(s, clock, 0.4)
        return s

    def test_registry_has_at_least_five_animations(self):
        self.assertGreaterEqual(len(animations.ANIMATIONS), 5)
        for required in ("bars", "mirror", "scope", "radial", "fire"):
            self.assertIn(required, animations.ANIMATIONS)
        self.assertEqual(animations.DEFAULT, "bars")
        self.assertIsInstance(animations.create("nope"), animations.ClassicBars)

    def test_every_animation_renders_inside_the_canvas(self):
        s = self.loud_spectrum()
        for anim_id in animations.ANIMATIONS:
            for w, h in ((420, 220), (900, 400)):
                with self.subTest(anim=anim_id, size=(w, h)):
                    shapes = animations.create(anim_id).render(s, w, h)
                    self.assertTrue(shapes)
                    for sh in shapes:
                        self.assertIn(sh.kind, ("rect", "line", "oval", "poly"))
                        self.assertIn(sh.role, ("low", "mid", "high", "peak", "line", "grid"))
                        self.assertTrue(0.0 <= sh.intensity <= 1.0001)
                        xs, ys = sh.coords[0::2], sh.coords[1::2]
                        self.assertTrue(all(-8 <= x <= w + 8 for x in xs), anim_id)
                        self.assertTrue(all(-8 <= y <= h + 8 for y in ys), anim_id)

    def test_shape_counts_are_bounded(self):
        s = self.loud_spectrum()
        for anim_id in animations.ANIMATIONS:
            with self.subTest(anim=anim_id):
                self.assertLessEqual(len(animations.create(anim_id).render(s, 900, 400)), 4 * spectrum.BANDS * 2 + 4)

    def test_classic_bars_colour_zones(self):
        s = self.loud_spectrum()
        roles = {sh.role for sh in animations.ClassicBars().render(s, 600, 300)}
        self.assertTrue({"low", "mid", "high", "peak"} <= roles)

    def test_silent_spectrum_still_renders_baseline(self):
        s = Spectrum(clock=Clock())
        for anim_id in ("bars", "mirror", "scope", "radial", "area"):
            with self.subTest(anim=anim_id):
                self.assertTrue(animations.create(anim_id).render(s, 400, 200))
        self.assertEqual(animations.Fire().render(s, 400, 200), [])


if __name__ == "__main__":
    unittest.main()
