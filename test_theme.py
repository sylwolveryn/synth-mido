"""Tesztek a theme modulhoz (unittest; pytest is futtatja).

Futtatás:  python -m unittest test_theme -v
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import theme


class PaletteTests(unittest.TestCase):
    def test_palettes_have_same_keys(self):
        self.assertEqual(set(theme.LIGHT), set(theme.DARK))

    def test_required_tokens_present(self):
        for key in ("bg", "surface", "fg", "border", "accent", "piano_bg",
                    "key_white", "key_black", "key_white_active", "key_black_active",
                    "log_bg", "log_fg"):
            self.assertIn(key, theme.LIGHT)

    def test_palette_for_unknown_uses_fallback(self):
        self.assertIs(theme.palette_for("bogus"), theme.PALETTES[theme.FALLBACK_SCHEME])

    def test_default_mode_is_system(self):
        self.assertEqual(theme.DEFAULT_MODE, theme.SYSTEM_MODE)


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "sub" / "settings.json"

    def test_missing_file_defaults_to_system(self):
        self.assertEqual(theme.load_mode(self.path), theme.SYSTEM_MODE)

    def test_save_and_load_roundtrip(self):
        for mode in theme.MODES:
            self.assertTrue(theme.save_mode(mode, self.path))
            self.assertEqual(theme.load_mode(self.path), mode)

    def test_corrupt_file_defaults_to_system(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(theme.load_mode(self.path), theme.SYSTEM_MODE)

    def test_invalid_mode_value_defaults_to_system(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"theme": "purple"}), encoding="utf-8")
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
