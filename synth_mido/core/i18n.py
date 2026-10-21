"""Többnyelvűség: egyszerű kulcs–érték fordítások.

Minden nyelv egy lapos JSON fájl a `synth_mido/lang/` mappában (`<kód>.json`,
`{"kulcs": "szöveg"}`), így később könnyen adatbázisba költöztethető. A magyar
a referencia: minden nyelvnek pontosan ugyanazok a kulcsai vannak. A szövegekben
`{név}` helyőrzők lehetnek (`str.format`). Hiányzó kulcsnál a magyar szöveg, ha az
sincs, maga a kulcs jelenik meg.

Nyelvváltáskor az egész nyelv újratöltődik — a program kicsi, ez nem gond.
"""

import json
from pathlib import Path
from typing import Dict, Optional

LANG_DIR = Path(__file__).resolve().parents[1] / "lang"
REFERENCE = "hu"
LANGUAGES = ("hu", "en", "fr", "ja", "de", "sv", "fi", "es", "tlh")  # a választó sorrendje
NAME_KEY = "language.name"   # a nyelv saját neve (pl. "Deutsch") — minden fájlban
CASE_SENSITIVE = {"tlh"}     # a klingon helyesírásban a kis- és nagybetű más-más hang: nem írjuk nagybetűvel

_cache: Dict[str, Dict[str, str]] = {}
_current = REFERENCE


def load_file(code: str, directory: Optional[Path] = None) -> Dict[str, str]:
    """Egy nyelv kulcs–érték párjai; hiányzó vagy hibás fájlra üres szótár."""
    path = Path(directory or LANG_DIR) / f"{code}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}


def _strings(code: str) -> Dict[str, str]:
    if code not in _cache:
        _cache[code] = load_file(code)
    return _cache[code]


def set_language(code: str) -> str:
    """Nyelv váltása (újratöltéssel); ismeretlen kódnál a magyar. Visszaadja az érvényes kódot."""
    global _current
    code = code if code in LANGUAGES else REFERENCE
    _cache.pop(code, None)
    _current = code
    _strings(code)
    return code


def current() -> str:
    return _current


def language_name(code: str) -> str:
    return _strings(code).get(NAME_KEY, code)


def upper(text: str) -> str:
    """Nagybetűs változat (szakaszcímek, fejléc) — kivéve, ha a nyelvben a betű mérete jelentést hordoz."""
    return text if _current in CASE_SENSITIVE else text.upper()


def t(key: str, **values) -> str:
    """A kulcs szövege az aktuális nyelven (tartalék: magyar, majd a kulcs), a helyőrzők kitöltésével."""
    text = _strings(_current).get(key) or _strings(REFERENCE).get(key) or key
    if not values:
        return text
    try:
        return text.format(**values)
    except (KeyError, IndexError, ValueError):
        return text
