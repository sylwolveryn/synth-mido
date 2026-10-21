"""Tesztek a megjelenés beállításokhoz: skin választás mentése, régi beállítás, OS felismerés.

Futtatás:  python -m unittest tests.test_theme -v
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from synth_mido.skins import theme


class SkinSettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "sub" / "settings.json"

    def write(self, data):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data), encoding="utf-8")

    def test_missing_file_starts_on_synthwave_dark(self):
        self.assertEqual(theme.load_skin(self.path), ("synthwave", theme.DARK))

    def test_old_theme_setting_no_longer_overrides_synthwave(self):
        # TASK-013: a régi "theme" kulcs (pl. "system") miatt nem a Synthwave indult
        self.write({"theme": "system", "visual_fx": False})
        self.assertEqual(theme.load_skin(self.path), ("synthwave", theme.DARK))

    def test_save_and_load_roundtrip_keeps_other_keys(self):
        self.write({"visual_fx": False})
        self.assertTrue(theme.save_skin("arcade", theme.LIGHT, self.path))
        self.assertEqual(theme.load_skin(self.path), ("arcade", theme.LIGHT))
        self.assertFalse(theme.load_setting("visual_fx", True, self.path))
        self.assertTrue(theme.save_skin("ocean", theme.SYSTEM, self.path))
        self.assertEqual(theme.load_skin(self.path), ("ocean", theme.SYSTEM))

    def test_unknown_values_fall_back(self):
        self.write({"skin": "purple", "skin_variant": "neon"})
        self.assertEqual(theme.load_skin(self.path), ("synthwave", theme.DARK))
        self.assertFalse(theme.save_skin("purple", theme.DARK, self.path))
        self.assertFalse(theme.save_skin("arcade", "neon", self.path))

    def test_corrupt_file(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(theme.load_skin(self.path), ("synthwave", theme.DARK))


class DetectionTests(unittest.TestCase):
    def test_linux_dark(self):
        with mock.patch.object(theme.sys, "platform", "linux"), \
             mock.patch.object(theme, "_run", return_value="'prefer-dark'"):
            self.assertEqual(theme.detect_system_theme(), theme.DARK)

    def test_linux_light(self):
        with mock.patch.object(theme.sys, "platform", "linux"), \
             mock.patch.object(theme, "_run", return_value="'default'"):
            self.assertEqual(theme.detect_system_theme(), theme.LIGHT)

    def test_macos_dark(self):
        with mock.patch.object(theme.sys, "platform", "darwin"), \
             mock.patch.object(theme, "_run", return_value="Dark"):
            self.assertEqual(theme.detect_system_theme(), theme.DARK)

    def test_windows_uses_registry_value(self):
        with mock.patch.object(theme.sys, "platform", "win32"):
            with mock.patch.object(theme, "_detect_windows", return_value=theme.DARK):
                self.assertEqual(theme.detect_system_theme(), theme.DARK)

    def test_failure_falls_back_without_raising(self):
        with mock.patch.object(theme.sys, "platform", "linux"), \
             mock.patch.object(theme, "_run", side_effect=FileNotFoundError):
            self.assertEqual(theme.detect_system_theme(), theme.FALLBACK_SCHEME)

    def test_resolve_scheme(self):
        self.assertEqual(theme.resolve_scheme(theme.DARK), theme.DARK)
        self.assertEqual(theme.resolve_scheme(theme.LIGHT), theme.LIGHT)
        with mock.patch.object(theme, "detect_system_theme", return_value=theme.DARK):
            self.assertEqual(theme.resolve_scheme(theme.SYSTEM), theme.DARK)


if __name__ == "__main__":
    unittest.main()
