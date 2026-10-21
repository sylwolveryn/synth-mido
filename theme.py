"""Téma (világos / sötét / rendszer) — színpaletták, OS-észlelés és beállítások mentése."""

import json
import os
import subprocess
import sys
from pathlib import Path

LIGHT_MODE = "light"
DARK_MODE = "dark"
SYSTEM_MODE = "system"
MODES = (SYSTEM_MODE, LIGHT_MODE, DARK_MODE)
DEFAULT_MODE = SYSTEM_MODE

# Ha az OS színsémája nem olvasható, világos témát használunk.
FALLBACK_SCHEME = LIGHT_MODE

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10

LIGHT = {
    "bg": "#f3f4f6",
    "surface": "#ffffff",
    "fg": "#1f2328",
    "muted": "#59636e",
    "border": "#d0d7de",
    "accent": "#2563eb",
    "accent_fg": "#ffffff",
    "select_bg": "#bfdbfe",
    "piano_bg": "#e5e7eb",
    "key_white": "#ffffff",
    "key_black": "#1f2937",
    "key_white_active": "#bfdbfe",
    "key_black_active": "#2563eb",
    "key_outline": "#6b7280",
    "key_label": "#4b5563",
    "log_bg": "#ffffff",
    "log_fg": "#1f2328",
}

DARK = {
    "bg": "#1e1f22",
    "surface": "#2b2d31",
    "fg": "#e6e6e6",
    "muted": "#a0a4ab",
    "border": "#3f4248",
    "accent": "#5b8def",
    "accent_fg": "#ffffff",
    "select_bg": "#2f4a7d",
    "piano_bg": "#2b2b2b",
    "key_white": "#f5f5f5",
    "key_black": "#111111",
    "key_white_active": "#a9c4ff",
    "key_black_active": "#7aa2ff",
    "key_outline": "#333333",
    "key_label": "#555555",
    "log_bg": "#17181a",
    "log_fg": "#d4d4d4",
}

PALETTES = {LIGHT_MODE: LIGHT, DARK_MODE: DARK}


def palette_for(scheme: str) -> dict:
    """A 'light' / 'dark' sémához tartozó paletta (ismeretlen esetén a fallback)."""
    return PALETTES.get(scheme, PALETTES[FALLBACK_SCHEME])


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
    return LIGHT_MODE if value else DARK_MODE


def _run(cmd):
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=2, check=False
    ).stdout.strip()


def _detect_macos():
    out = _run(["defaults", "read", "-g", "AppleInterfaceStyle"])
    return DARK_MODE if out.lower() == "dark" else LIGHT_MODE


def _detect_linux():
    out = _run(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"]).lower()
    if "dark" in out:
        return DARK_MODE
    if "light" in out or "default" in out:
        return LIGHT_MODE
    # régebbi GNOME: GTK téma neve
    out = _run(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"]).lower()
    if "dark" in out:
        return DARK_MODE
    return LIGHT_MODE


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


def resolve_scheme(mode: str) -> str:
    """Mód ('system'/'light'/'dark') -> konkrét séma ('light'/'dark')."""
    if mode == SYSTEM_MODE:
        return detect_system_theme()
    if mode in PALETTES:
        return mode
    return detect_system_theme()


def settings_path() -> Path:
    base = os.environ.get("APPDATA") if sys.platform.startswith("win") else None
    if not base:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "synth-mido" / "settings.json"


def load_mode(path=None) -> str:
    """Mentett téma-mód; hiányzó / hibás fájl esetén System."""
    try:
        data = json.loads(Path(path or settings_path()).read_text(encoding="utf-8"))
        mode = data.get("theme")
        if mode in MODES:
            return mode
    except Exception:
        pass
    return DEFAULT_MODE


def save_mode(mode: str, path=None) -> bool:
    """Téma-mód mentése; True, ha sikerült."""
    if mode not in MODES:
        return False
    target = Path(path or settings_path())
    try:
        data = {}
        try:
            loaded = json.loads(target.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            pass
        data["theme"] = mode
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except OSError:
        return False
