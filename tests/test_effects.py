"""Tesztek a hangeffektekhez (ablak nélkül): nyilvántartás, skin párosítás, minden effekt közös
viselkedése, a láng, a szirom és a gőz saját mozgása, valamint a beállítás mentés.

Futtatás:  python -m unittest tests.test_effects -v
"""

import math
import tempfile
import unittest
from pathlib import Path

from synth_mido.core import i18n, piano_layout
from synth_mido.fx import effects
from synth_mido.fx.effects import fire
from synth_mido.skins import catalog, registry, theme  # noqa: F401 — a catalog regisztrálja a skineket

H = 96.0
W = 1040.0
KEYS = {k.note: k for k in piano_layout.layout(W, 150)}
KINDS = {"poly", "oval", "rect", "ring", "text"}


def span(note):
    k = KEYS.get(note)
    return (k.x0, k.x1, k.black) if k else None


def of(role, shapes):
    return [s for s in shapes if s.role == role]


def ys(shape):
    return shape.points[1::2]


def run(effect, notes=(60, 64, 67), hold=1.0, after=0.0, fps=30):
    """Hangok lenyomása 0-kor, elengedés `hold`-kor, képkockák a végéig; az utolsó képkocka alakzatai."""
    for n in notes:
        effect.note_on(n, 110, t=0.0)
    shapes, t = [], 0.0
    released = False
    while t <= hold + after:
        if not released and t >= hold:
            for n in notes:
                effect.note_off(n, t=t)
            released = True
        shapes = effect.frame(t, W, H, span)
        t += 1 / fps
    return shapes


class RegistryTests(unittest.TestCase):
    def test_fourteen_effects_registered(self):
        self.assertEqual(effects.ids(), ["neon", "flames", "petals", "leaves", "steam", "dust", "bubbles", "snow",
                                         "stars", "pixels", "math", "roman", "notes", "compass"])

    def test_every_skin_names_a_registered_effect(self):
        mapping = {s.id: s.effect for s in registry.all_skins()}
        self.assertEqual(len(mapping), 17)
        self.assertTrue(set(mapping.values()) <= set(effects.ids()))
        self.assertEqual((mapping["volcano"], mapping["sakura"], mapping["steampunk"]), ("flames", "petals", "steam"))

    def test_unknown_id_falls_back_and_duplicates_are_refused(self):
        self.assertIsInstance(effects.create("nincs"), effects.EFFECTS[effects.DEFAULT])
        with self.assertRaises(ValueError):
            effects.register(fire.Flames)

    def test_every_effect_has_a_name_in_every_language(self):
        for code in i18n.LANGUAGES:
            strings = i18n.load_file(code)
            for effect_id in effects.ids():
                self.assertIn(f"fx.{effect_id}", strings, code)

    def test_roles_are_declared_and_coloured_in_every_skin(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            self.assertEqual(set(fx.KINDS), set(fx.LAYERS), cls.id)
            self.assertTrue(set(fx.KINDS.values()) <= KINDS, cls.id)
            self.assertTrue(set(fx.SMOOTH) <= set(fx.LAYERS), cls.id)
            for skin in registry.all_skins():
                for scheme in ("dark", "light"):
                    colors = fx.colors(skin.palette(scheme), scheme == "dark")
                    self.assertEqual(set(colors), set(fx.LAYERS), (cls.id, skin.id))
                    for white, black in colors.values():
                        self.assertRegex(white, r"^#[0-9a-fA-F]{6}$")
                        self.assertRegex(black, r"^#[0-9a-fA-F]{6}$")


class SharedBehaviourTests(unittest.TestCase):
    """Minden regisztrált effekt ugyanúgy viselkedik a felület felé."""

    def test_idle_draws_nothing(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            self.assertFalse(fx.active)
            self.assertEqual(fx.frame(0, W, H, span), [], cls.id)

    def test_held_notes_draw_valid_shapes_in_layer_order(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            shapes = run(fx, hold=2.0)
            self.assertTrue(shapes, cls.id)
            order = [fx.LAYERS.index(s.role) for s in shapes]
            self.assertEqual(order, sorted(order), cls.id)
            for s in shapes:
                kind = fx.KINDS[s.role]
                self.assertEqual(len(s.points), 2 if kind == "text" else (len(s.points) if kind == "poly" else 4))
                self.assertTrue(0 < s.intensity <= 1.2, (cls.id, s))
                if kind == "text":
                    self.assertTrue(s.text and 0 < s.size <= fx.FONT_SIZE_MAX, cls.id)
                self.assertTrue(all(-60 <= y <= H + 60 for y in ys(s)), (cls.id, s.role, s.points))

    def test_everything_dies_down_after_release(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            run(fx, hold=0.5, after=max(cls.RELEASE, cls.LIFE) + 0.5)
            self.assertFalse(fx.active, cls.id)

    def test_caps_limit_objects(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            for i in range(400):
                note = 21 + i % 88
                fx.note_on(note, 100, t=i * 0.002)
                if i % 3:
                    fx.note_off(note, t=i * 0.002 + 0.001)
            for k in range(30):
                fx.frame(0.8 + k / 30, W, H, span)
            self.assertLessEqual(len(fx.voices), cls.MAX_VOICES, cls.id)
            self.assertLessEqual(len(fx.particles), cls.MAX_PARTICLES, cls.id)

    def test_sounding_note_survives_the_caps(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            fx.note_on(60, 100, t=0)
            for i in range(cls.MAX_VOICES + 20):
                fx.note_on(70, 100, t=0.001 * i)
                fx.note_off(70, t=0.001 * i)
            self.assertIn(60, [v.note for v in fx.voices], cls.id)

    def test_notes_outside_the_keyboard_are_ignored(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            fx.note_on(12, 100, t=0)
            self.assertEqual(fx.frame(0.2, W, H, span), [], cls.id)

    def test_clear(self):
        for cls in effects.EFFECTS.values():
            fx = cls()
            run(fx, hold=0.3)
            fx.clear()
            self.assertFalse(fx.active, cls.id)


class FlameTests(unittest.TestCase):
    def setUp(self):
        self.fx = effects.create("flames", clock=lambda: 0.0)

    def test_note_on_lights_a_glowing_flame_with_embers(self):
        self.fx.note_on(60, 100, t=0.0)
        roles = [s.role for s in self.fx.frame(0.1, W, H, span)]
        self.assertEqual(roles.count("halo"), len(fire.Flames.HALOS))
        self.assertEqual((roles.count("flame"), roles.count("core")), (1, 1))
        self.assertEqual(roles.count("ember"), fire.Flames.BURST)

    def test_flame_flares_up_then_flickers_and_stands_on_its_key(self):
        self.fx.note_on(60, 100, t=0)
        flames = [of("flame", self.fx.frame(t, W, H, span))[0] for t in (0.02, 0.2, 0.33, 0.47)]
        heights = [H - min(ys(f)) for f in flames]
        self.assertLess(heights[0], heights[1])
        self.assertGreater(len({round(h, 1) for h in heights[1:]}), 1)
        self.assertEqual(max(ys(flames[1])), H)

    def test_velocity_sets_height(self):
        self.fx.note_on(60, 20, t=0)
        self.fx.note_on(72, 127, t=0)
        quiet, loud = sorted(of("flame", self.fx.frame(0.2, W, H, span)), key=lambda f: f.intensity)
        self.assertLess(H - min(ys(quiet)), H - min(ys(loud)))


class NeonTests(unittest.TestCase):
    def test_bar_grows_from_the_key_and_detaches_after_release(self):
        fx = effects.create("neon")
        fx.note_on(60, 100, t=0)
        bar = of("bar", fx.frame(0.2, W, H, span))[0]
        k = KEYS[60]
        self.assertEqual((bar.points[0], bar.points[2], bar.points[3]), (k.x0, k.x1, H))
        fx.note_off(60, t=0.3)
        bar = of("bar", fx.frame(0.5, W, H, span))[0]
        self.assertLess(bar.points[3], H)


class PetalTests(unittest.TestCase):
    def test_petals_drift_away_from_the_keys_slowly_and_spin(self):
        fx = effects.create("petals")
        fx.note_on(60, 100, t=0)
        first = {id(p): p for p in fx.particles}
        a = fx.frame(0.1, W, H, span)
        b = fx.frame(1.5, W, H, span)
        pa = [s for s in a if s.role.startswith("petal")][:len(first)]
        pb = [s for s in b if s.role.startswith("petal")][:len(first)]

        def centre(s):
            return sum(s.points[0::2]) / (len(s.points) / 2), sum(ys(s)) / (len(s.points) / 2)
        for sa, sb in zip(pa, pb):
            (xa, ya), (xb, yb) = centre(sa), centre(sb)
            self.assertLess(yb, ya)                          # felfelé száll
            self.assertGreater(xb, xa - 15)                  # a szél jobbra (vagy legfeljebb imbolyog)
            self.assertLess(abs(yb - ya), 1.6 * 60)          # lassan: < 60 px / mp
        self.assertGreaterEqual(effects.EFFECTS["petals"].LIFE, 3.0)   # sokáig lebeg

    def test_petal_shape_is_a_notched_smooth_polygon(self):
        fx = effects.create("petals")
        self.assertEqual(set(fx.SMOOTH), {"petal", "petal_light"})
        fx.note_on(60, 100, t=0)
        petal = [s for s in fx.frame(0.2, W, H, span) if s.role.startswith("petal")][0]
        self.assertEqual(len(petal.points), 16)


class SteamTests(unittest.TestCase):
    def test_puffs_rise_expand_and_thin_out(self):
        fx = effects.create("steam")
        fx.note_on(60, 100, t=0)
        early = of("puff", fx.frame(0.15, W, H, span))
        late = of("puff", fx.frame(1.2, W, H, span))
        self.assertEqual(len(early), effects.EFFECTS["steam"].BURST)

        def radius(s):
            return (s.points[2] - s.points[0]) / 2
        self.assertGreater(max(map(radius, late)), max(map(radius, early)))
        self.assertLess(min(min(ys(s)) for s in late), min(min(ys(s)) for s in early))
        self.assertLess(max(s.intensity for s in late[:6]), max(s.intensity for s in early))

    def test_burst_on_press_then_steady_vapour_while_held(self):
        fx = effects.create("steam")
        fx.note_on(60, 100, t=0)
        burst = len(fx.particles)
        for k in range(1, 31):
            fx.frame(k / 30, W, H, span)
        self.assertGreater(len(fx.particles), burst)          # amíg szól, gőzöl


class GlyphTests(unittest.TestCase):
    def test_glyph_sets(self):
        for effect_id, sample in (("math", "π"), ("roman", "Ⅹ"), ("notes", "♪"), ("compass", "✦")):
            fx = effects.create(effect_id)
            self.assertIn(sample, fx.GLYPHS)
            fx.note_on(60, 100, t=0)
            texts = [s.text for s in fx.frame(0.3, W, H, span) if s.role == "glyph"]
            self.assertTrue(texts and all(t in fx.GLYPHS for t in texts), effect_id)


class PixelTests(unittest.TestCase):
    def test_pixels_snap_to_the_grid(self):
        fx = effects.create("pixels")
        shapes = run(fx, hold=0.6)
        for s in shapes:
            if s.role != "block":
                self.assertEqual(s.points[0] % 6, 0)
                self.assertTrue(math.isclose(s.points[1] % 6, 0, abs_tol=1e-9))


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
