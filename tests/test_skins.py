"""Tesztek a skin rendszerhez: nyilvántartás, paletták (kontraszt), fejléc rajzolók, stílus tokenek.

Futtatás:  python -m unittest tests.test_skins -v
"""

import unittest

from synth_mido.skins import catalog, registry  # noqa: F401  (catalog: regisztráció)
from synth_mido.skins.palette import TOKENS, check, contrast, ensure_contrast, make_palette, mix
from synth_mido.skins.registry import Skin

NEW_SKINS = {"astronaut", "safari", "cartography", "mathematics", "antiquity", "ocean", "forest", "sakura",
             "steampunk", "arcade", "artdeco", "desert", "arctic", "volcano", "jazz"}


class FakeCanvas:
    """A rajzolók hívásait számolja (nincs szükség valódi ablakra)."""

    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        if not name.startswith("create_"):
            raise AttributeError(name)

        def record(*args, **kwargs):
            coords = [a for a in args if isinstance(a, (int, float))]
            self.calls.append((name, coords, kwargs))
            return len(self.calls)

        return record


class RegistryTests(unittest.TestCase):
    def test_synthwave_classic_and_15_new_skins(self):
        ids = {s.id for s in registry.all_skins()}
        self.assertTrue(NEW_SKINS <= ids)
        self.assertEqual(len(NEW_SKINS), 15)
        self.assertEqual(ids - NEW_SKINS, {"synthwave", "classic"})
        self.assertEqual(registry.all_skins()[0].id, "synthwave")

    def test_default_is_synthwave_dark(self):
        self.assertEqual((registry.DEFAULT_SKIN, registry.DEFAULT_VARIANT), ("synthwave", registry.DARK))
        self.assertEqual(registry.get("does-not-exist").id, "synthwave")

    def test_names_unique_and_lookup(self):
        names = [s.name for s in registry.all_skins()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(registry.by_name("Űrhajós").id, "astronaut")
        self.assertIsNone(registry.by_name("nincs ilyen"))

    def test_duplicate_registration_rejected(self):
        with self.assertRaises(ValueError):
            registry.register(Skin("synthwave", "Másik", {}, {}))

    def test_variant_lookup(self):
        s = registry.get("ocean")
        self.assertIs(s.palette(registry.LIGHT), s.light)
        self.assertIs(s.palette(registry.DARK), s.dark)

    def test_choose_font(self):
        self.assertEqual(registry.choose_font(("Nope", "Georgia"), ["Arial", "Georgia"]), "Georgia")
        self.assertEqual(registry.choose_font(("Nope",), ["Arial"]), "Segoe UI")


class PaletteTests(unittest.TestCase):
    def test_every_variant_has_all_tokens_and_passes_contrast(self):
        for skin in registry.all_skins():
            for scheme in (registry.DARK, registry.LIGHT):
                p = skin.palette(scheme)
                with self.subTest(skin=skin.id, scheme=scheme):
                    self.assertEqual(set(TOKENS) - set(p), set())
                    self.assertEqual(check(p), [])

    def test_dark_and_light_variants_differ(self):
        for skin in registry.all_skins():
            with self.subTest(skin=skin.id):
                self.assertNotEqual(skin.dark["bg"], skin.light["bg"])
                self.assertLess(contrast(skin.dark["bg"], "#000000"), contrast(skin.light["bg"], "#000000"))

    def test_skins_are_distinct(self):
        accents = {(s.dark["bg"], s.dark["accent"]) for s in registry.all_skins()}
        self.assertEqual(len(accents), len(registry.all_skins()))

    def test_synthwave_night_keeps_agreed_tokens(self):
        p = registry.get("synthwave").dark
        self.assertEqual((p["bg"], p["surface"], p["accent"], p["accent2"]), ("#0d0221", "#261447", "#ff2a6d", "#05d9e8"))

    def test_builder_fixes_low_contrast(self):
        p = make_palette("#ffffff", "#ffffff", "#dddddd", "#ffee00", "#ffff99", ("#fff", "#fff", "#fff"), "#eeeeee")
        self.assertEqual(check(p), [])

    def test_helpers(self):
        self.assertAlmostEqual(contrast("#000000", "#ffffff"), 21.0, places=1)
        self.assertEqual(mix("#000000", "#ffffff", 0.5), "#808080")
        self.assertGreaterEqual(contrast(ensure_contrast("#777777", ["#808080"]), "#808080"), 4.5)


class PainterTests(unittest.TestCase):
    def test_every_skin_paints_a_scene_in_both_variants_and_sizes(self):
        for skin in registry.all_skins():
            for scheme in (registry.DARK, registry.LIGHT):
                for width in (760, 1200):
                    with self.subTest(skin=skin.id, scheme=scheme, width=width):
                        canvas = FakeCanvas()
                        skin.painter(canvas, width, skin.header_height, skin.palette(scheme), "Segoe UI",
                                     scheme == registry.DARK)
                        minimum = 3 if skin.id == "classic" else 20
                        self.assertGreaterEqual(len(canvas.calls), minimum)
                        texts = [kw.get("text", "") for name, _, kw in canvas.calls if name == "create_text"]
                        self.assertTrue(any("SYNTH" in t.upper().replace(" ", "") for t in texts))

    def test_scene_scales_with_width(self):
        skin = registry.get("forest")
        narrow, wide = FakeCanvas(), FakeCanvas()
        skin.painter(narrow, 760, 92, skin.dark, "Segoe UI", True)
        skin.painter(wide, 1400, 92, skin.dark, "Segoe UI", True)
        max_x = lambda c: max(x for _, coords, _ in c.calls for x in coords[::2] if coords)  # noqa: E731
        self.assertGreater(max_x(wide), max_x(narrow))


class WidgetStyleTests(unittest.TestCase):
    def test_style_tokens_reference_palette_tokens(self):
        for skin in registry.all_skins():
            st = skin.style
            with self.subTest(skin=skin.id):
                self.assertIn(st.button_edge, TOKENS)
                self.assertIn(st.relief, ("flat", "solid", "raised", "ridge", "groove", "sunken"))
                self.assertIn(st.frame_relief, ("flat", "solid", "raised", "ridge", "groove", "sunken"))
                self.assertEqual(len(st.button_padding), 2)
                self.assertGreaterEqual(st.border_width, 1)

    def test_skins_have_different_widget_shapes(self):
        shapes = {(s.style.relief, s.style.border_width, s.style.button_padding, s.style.title_upper)
                  for s in registry.all_skins()}
        self.assertGreaterEqual(len(shapes), 6)


if __name__ == "__main__":
    unittest.main()
