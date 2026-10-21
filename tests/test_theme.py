"""Tesztek a theme modulhoz (unittest; pytest is futtatja).

Futtatás:  python -m unittest test_theme -v
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from synth_mido.skins import theme


class PaletteTests(unittest.TestCase):
    def test_palettes_have_same_keys(self):
        self.assertEqual(set(theme.LIGHT), set(theme.DARK))
        self.assertEqual(set(theme.SYNTHWAVE), set(theme.LIGHT))

    def test_required_tokens_present(self):
        for key in ("bg", "surface", "fg", "border", "accent", "piano_bg",
                    "key_white", "key_black", "key_white_active", "key_black_active",
                    "log_bg", "log_fg"):
            self.assertIn(key, theme.LIGHT)

    def test_palette_for_unknown_uses_fallback(self):
        self.assertIs(theme.palette_for("bogus"), theme.PALETTES[theme.FALLBACK_SCHEME])

    def test_default_mode_is_synthwave(self):
        # TASK-009: a Synthwave dizájn lett az alapértelmezett (korábban: Rendszer)
        self.assertEqual(theme.DEFAULT_MODE, theme.SYNTHWAVE_MODE)
        self.assertEqual(theme.MODES[0], theme.SYNTHWAVE_MODE)


class SynthwaveTests(unittest.TestCase):
    P = theme.SYNTHWAVE

    def test_agreed_tokens(self):
        self.assertEqual(self.P["bg"], "#0d0221")
        self.assertEqual(self.P["surface"], "#261447")
        self.assertEqual(self.P["accent"], "#ff2a6d")
        self.assertEqual(self.P["accent2"], "#05d9e8")
        self.assertEqual((self.P["sun_top"], self.P["sun_mid"]), ("#fdd835", "#ff9e00"))

    def test_text_contrast_at_least_4_5(self):
        pairs = [
            ("fg", "bg"), ("fg", "surface"), ("muted", "bg"), ("muted", "surface"),
            ("accent_fg", "accent"), ("log_fg", "log_bg"), ("section_fg", "bg"),
            ("title_fg", "header_bg"), ("fg", "select_bg"), ("key_label", "key_white"),
        ]
        for fg, bg in pairs:
            ratio = theme.contrast(self.P[fg], self.P[bg])
            self.assertGreaterEqual(ratio, 4.5, f"{fg} on {bg}: {ratio:.2f}")

    def test_resolves_to_itself(self):
        self.assertEqual(theme.resolve_scheme(theme.SYNTHWAVE_MODE), theme.SYNTHWAVE_MODE)
        self.assertIs(theme.palette_for(theme.SYNTHWAVE_MODE), theme.SYNTHWAVE)

    def test_contrast_helper(self):
        self.assertAlmostEqual(theme.contrast("#000000", "#ffffff"), 21.0, places=1)
        self.assertAlmostEqual(theme.contrast("#777777", "#777777"), 1.0)

    def test_mix(self):
        self.assertEqual(theme.mix("#000000", "#ffffff", 0.5), "#808080")
        self.assertEqual(theme.mix("#fdd835", "#ff2a6d", 0), "#fdd835")
        self.assertEqual(theme.mix("#fdd835", "#ff2a6d", 1), "#ff2a6d")

    def test_display_font_prefers_bahnschrift(self):
        self.assertEqual(theme.display_font(["Arial", "Bahnschrift", "Segoe UI"]), "Bahnschrift")
        self.assertEqual(theme.display_font(["Arial", "DejaVu Sans"]), "DejaVu Sans")
        self.assertEqual(theme.display_font(["Arial"]), theme.FONT_FAMILY)


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "sub" / "settings.json"

    def test_missing_file_uses_default(self):
        self.assertEqual(theme.load_mode(self.path), theme.DEFAULT_MODE)

    def test_save_and_load_roundtrip(self):
        for mode in theme.MODES:
            self.assertTrue(theme.save_mode(mode, self.path))
            self.assertEqual(theme.load_mode(self.path), mode)

    def test_corrupt_file_uses_default(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(theme.load_mode(self.path), theme.DEFAULT_MODE)

    def test_invalid_mode_value_uses_default(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"theme": "purple"}), encoding="utf-8")
        self.assertEqual(theme.load_mode(self.path), theme.DEFAULT_MODE)

    def test_saved_system_choice_is_still_respected(self):
        theme.save_mode(theme.SYSTEM_MODE, self.path)
        self.assertEqual(theme.load_mode(self.path), theme.SYSTEM_MODE)

    def test_save_rejects_invalid_mode(self):
        self.assertFalse(theme.save_mode("purple", self.path))
        self.assertFalse(self.path.exists())

    def test_save_keeps_other_keys(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"other": 1}), encoding="utf-8")
        theme.save_mode(theme.DARK_MODE, self.path)
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(data, {"other": 1, "theme": "dark"})


class DetectionTests(unittest.TestCase):
    def test_linux_dark(self):
        with mock.patch.object(theme.sys, "platform", "linux"), \
             mock.patch.object(theme, "_run", return_value="'prefer-dark'"):
            self.assertEqual(theme.detect_system_theme(), theme.DARK_MODE)

    def test_linux_light(self):
        with mock.patch.object(theme.sys, "platform", "linux"), \
             mock.patch.object(theme, "_run", return_value="'default'"):
            self.assertEqual(theme.detect_system_theme(), theme.LIGHT_MODE)

    def test_macos_dark(self):
        with mock.patch.object(theme.sys, "platform", "darwin"), \
             mock.patch.object(theme, "_run", return_value="Dark"):
            self.assertEqual(theme.detect_system_theme(), theme.DARK_MODE)

    def test_windows_uses_registry_value(self):
        with mock.patch.object(theme.sys, "platform", "win32"):
            with mock.patch.object(theme, "_detect_windows", return_value=theme.DARK_MODE):
                self.assertEqual(theme.detect_system_theme(), theme.DARK_MODE)

    def test_failure_falls_back_without_raising(self):
        with mock.patch.object(theme.sys, "platform", "linux"), \
             mock.patch.object(theme, "_run", side_effect=FileNotFoundError):
            self.assertEqual(theme.detect_system_theme(), theme.FALLBACK_SCHEME)

    def test_resolve_scheme(self):
        self.assertEqual(theme.resolve_scheme(theme.DARK_MODE), theme.DARK_MODE)
        self.assertEqual(theme.resolve_scheme(theme.LIGHT_MODE), theme.LIGHT_MODE)
        with mock.patch.object(theme, "detect_system_theme", return_value=theme.DARK_MODE):
            self.assertEqual(theme.resolve_scheme(theme.SYSTEM_MODE), theme.DARK_MODE)


if __name__ == "__main__":
    unittest.main()
