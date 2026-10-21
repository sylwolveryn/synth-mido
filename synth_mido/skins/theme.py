"""Megjelenés beállítások: a választott skin és változat (sötét / világos / rendszer),
az OS színsémájának felismerése és a settings.json kezelése.

A skinek maguk a `catalog` modulban vannak (Registry); itt csak a választás él.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from synth_mido.skins import (
    catalog,  # noqa: F401  (a skinek regisztrálása)
    registry,
)
from synth_mido.skins.palette import contrast, mix  # noqa: F401  (kényelmi újraexport)
from synth_mido.skins.registry import (
    DARK,
    DEFAULT_SKIN,
    DEFAULT_VARIANT,
    LIGHT,
    SYSTEM,
    VARIANTS,
)

# Ha az OS színsémája nem olvasható, világos változatot használunk.
FALLBACK_SCHEME = LIGHT

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10

# A beállítás kulcsai. Új kulcs (TASK-013): a régi "theme" értéket szándékosan
# figyelmen kívül hagyjuk, így mindenki egyszer a Synthwave skinnel indul.
SKIN_KEY = "skin"
VARIANT_KEY = "skin_variant"


def _detect_windows():
    import winreg

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
    )
    try:
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
    finally:
        winreg.CloseKey(key)
    return LIGHT if value else DARK


def _run(cmd):
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=2, check=False
    ).stdout.strip()


def _detect_macos():
    out = _run(["defaults", "read", "-g", "AppleInterfaceStyle"])
    return DARK if out.lower() == "dark" else LIGHT


def _detect_linux():
    out = _run(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"]).lower()
    if "dark" in out:
        return DARK
    if "light" in out or "default" in out:
        return LIGHT
    # régebbi GNOME: GTK téma neve
    out = _run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"]).lower()
    if "dark" in out:
        return DARK
    return LIGHT


def detect_system_theme() -> str:
    """Az OS aktuális színsémája: 'light' vagy 'dark'.

    Hiba esetén FALLBACK_SCHEME ('light') — soha nem dob kivételt.
    """
    try:
        if sys.platform.startswith("win"):
            return _detect_windows()
        if sys.platform == "darwin":
            return _detect_macos()
        return _detect_linux()
    except Exception:
        return FALLBACK_SCHEME


def resolve_scheme(variant: str) -> str:
    """Változat ('dark'/'light'/'system') -> konkrét séma ('dark'/'light')."""
    if variant in (DARK, LIGHT):
        return variant
    return detect_system_theme()


# --- beállítások ---------------------------------------------------------------

def settings_path() -> Path:
    base = os.environ.get("APPDATA") if sys.platform.startswith("win") else None
    if not base:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "synth-mido" / "settings.json"


def load_setting(key: str, default=None, path=None):
    """Egy beállítás a settings.json-ból; hiányzó / hibás fájl esetén `default`."""
    try:
        data = json.loads(Path(path or settings_path()).read_text(encoding="utf-8"))
        if isinstance(data, dict) and key in data:
            return data[key]
    except Exception:
        pass
    return default


def save_setting(key: str, value, path=None) -> bool:
    """Egy beállítás mentése a többi megtartásával; True, ha sikerült."""
    target = Path(path or settings_path())
    try:
        data = {}
        try:
            loaded = json.loads(target.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            pass
        data[key] = value
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except OSError:
        return False


def load_skin(path=None):
    """(skin azonosító, változat) — ismeretlen / hiányzó értéknél Synthwave, sötét."""
    skin_id = load_setting(SKIN_KEY, DEFAULT_SKIN, path)
    variant = load_setting(VARIANT_KEY, DEFAULT_VARIANT, path)
    if registry.get(skin_id).id != skin_id:
        skin_id = DEFAULT_SKIN
    if variant not in VARIANTS:
        variant = DEFAULT_VARIANT
    return skin_id, variant


def save_skin(skin_id: str, variant: str, path=None) -> bool:
    if registry.get(skin_id).id != skin_id or variant not in VARIANTS:
        return False
    return save_setting(SKIN_KEY, skin_id, path) and save_setting(VARIANT_KEY, variant, path)


__all__ = [
    "DARK", "LIGHT", "SYSTEM", "VARIANTS", "DEFAULT_SKIN", "DEFAULT_VARIANT", "FONT_FAMILY", "FONT_SIZE",
    "detect_system_theme", "resolve_scheme", "settings_path", "load_setting", "save_setting", "load_skin",
    "save_skin", "contrast", "mix",
]
