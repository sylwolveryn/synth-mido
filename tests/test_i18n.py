"""Tesztek a többnyelvűséghez: a nyelvi fájlok kulcsai, helyőrzői és a tartalékok.

Futtatás:  python -m unittest tests.test_i18n -v
"""

import json
import re
import string
import tempfile
import unittest
from pathlib import Path

from synth_mido.core import doubling, i18n
from synth_mido.fx import animations
from synth_mido.skins import catalog, registry  # noqa: F401 — a catalog regisztrálja a skineket

ROOT = Path(__file__).resolve().parents[1]


def placeholders(text):
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


class LanguageFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = i18n.load_file(i18n.REFERENCE)

    def test_all_nine_languages_are_offered(self):
        self.assertEqual(i18n.LANGUAGES, ("hu", "en", "fr", "ja", "de", "sv", "fi", "es", "tlh"))
        names = [i18n.load_file(code)[i18n.NAME_KEY] for code in i18n.LANGUAGES]
        self.assertEqual(names, ["Magyar", "English", "Français", "日本語", "Deutsch", "Svenska", "Suomi", "Español",
                                 "tlhIngan Hol"])

    def test_files_are_flat_key_value_json(self):
        for code in i18n.LANGUAGES:
            data = json.loads((i18n.LANG_DIR / f"{code}.json").read_text(encoding="utf-8"))
            self.assertIsInstance(data, dict, code)
            self.assertTrue(all(isinstance(k, str) and isinstance(v, str) and v.strip() for k, v in data.items()), code)

    def test_every_language_has_exactly_the_reference_keys(self):
        for code in i18n.LANGUAGES:
            keys = set(i18n.load_file(code))
            self.assertEqual(sorted(set(self.reference) - keys), [], f"{code}: missing")
            self.assertEqual(sorted(keys - set(self.reference)), [], f"{code}: extra")

    def test_placeholders_match_the_reference(self):
        for code in i18n.LANGUAGES:
            strings = i18n.load_file(code)
            for key, text in self.reference.items():
                self.assertEqual(placeholders(strings[key]), placeholders(text), f"{code}: {key}")

    def test_every_key_used_in_the_code_exists(self):
        used = set()
        # t("kulcs"), tr(widget, "kulcs") és a kulcsként tárolt literálok (pl. a szakaszcímek)
        prefixes = "|".join(sorted({k.split(".")[0] for k in self.reference}))
        pattern = re.compile(r"""["']((?:%s)\.[a-z_]+(?:\.[a-z_]+)*)["']""" % prefixes)
        for path in (ROOT / "synth_mido").rglob("*.py"):
            used |= set(pattern.findall(path.read_text(encoding="utf-8")))
        self.assertGreater(len(used), 100)
        self.assertEqual(sorted(used - set(self.reference)), [])

    def test_generated_keys_exist(self):
        keys = set(self.reference)
        for mode in doubling.MODES:
            self.assertIn(f"doubling.{mode}", keys)
        for variant in registry.VARIANTS_ORDER:
            self.assertIn(f"variant.{variant}", keys)
        for skin in registry.all_skins():
            self.assertIn(f"skin.{skin.id}", keys)
        for anim_id in animations.ANIMATIONS:
            self.assertIn(f"eq.{anim_id}", keys)
        for col in ("name", "created", "duration", "notes", "instrument"):
            self.assertIn(f"records.col.{col}", keys)


class TranslatorTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(i18n.set_language, i18n.REFERENCE)

    def test_switching_reloads_everything(self):
        self.assertEqual(i18n.set_language("de"), "de")
        self.assertEqual(i18n.current(), "de")
        self.assertEqual(i18n.t("btn.save"), "Speichern")
        self.assertEqual(doubling.label(doubling.UP), "+1 Oktave")
        self.assertEqual(registry.variant_label(registry.DARK), "Dunkel")
        self.assertEqual(registry.get("forest").label, "Wald")
        self.assertEqual(animations.label("fire"), "Feuer")
        i18n.set_language("ja")
        self.assertEqual(i18n.t("btn.save"), "保存")

    def test_placeholders_are_filled(self):
        i18n.set_language("en")
        self.assertEqual(i18n.t("log.devices", inputs=2, outputs=3), "Devices: 2 inputs, 3 outputs")

    def test_unknown_language_falls_back_to_hungarian(self):
        self.assertEqual(i18n.set_language("xx"), "hu")
        self.assertEqual(i18n.t("btn.save"), "Mentés")

    def test_missing_key_falls_back_to_hungarian_then_to_the_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "hu.json").write_text(json.dumps({"a": "magyar"}), encoding="utf-8")
            self.assertEqual(i18n.load_file("hu", Path(tmp)), {"a": "magyar"})
            self.assertEqual(i18n.load_file("nincs", Path(tmp)), {})
        i18n.set_language("en")
        i18n._cache["en"] = {k: v for k, v in i18n._cache["en"].items() if k != "btn.save"}
        self.assertEqual(i18n.t("btn.save"), "Mentés")
        self.assertEqual(i18n.t("no.such.key"), "no.such.key")

    def test_bad_placeholder_does_not_crash(self):
        self.assertEqual(i18n.t("log.devices", wrong=1), i18n.load_file("hu")["log.devices"])

    def test_klingon_is_never_uppercased(self):
        i18n.set_language("tlh")
        self.assertEqual(i18n.upper("chu'qa'"), "chu'qa'")
        i18n.set_language("en")
        self.assertEqual(i18n.upper("Playback"), "PLAYBACK")

    def test_core_errors_follow_the_language(self):
        from synth_mido.core import recorder
        i18n.set_language("en")
        with self.assertRaisesRegex(ValueError, "Enter a name"):
            recorder.sanitize_name("  ")


if __name__ == "__main__":
    unittest.main()
