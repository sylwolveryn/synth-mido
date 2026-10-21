"""Téma (synthwave / világos / sötét / rendszer) — színpaletták, OS-észlelés és beállítások mentése."""

import json
import os
import subprocess
import sys
from pathlib import Path

SYNTHWAVE_MODE = "synthwave"
LIGHT_MODE = "light"
DARK_MODE = "dark"
SYSTEM_MODE = "system"
MODES = (SYNTHWAVE_MODE, SYSTEM_MODE, LIGHT_MODE, DARK_MODE)
DEFAULT_MODE = SYNTHWAVE_MODE  # TASK-009: az új dizájn az alapértelmezett

# Ha az OS színsémája nem olvasható, világos témát használunk.
FALLBACK_SCHEME = LIGHT_MODE

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10
# Synthwave: retró, keskeny betűtípus, ha a rendszerben van (Windows 10+: Bahnschrift)
DISPLAY_FONTS = ("Bahnschrift", "Segoe UI", "DejaVu Sans")

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
    "accent2": "#0ea5e9",
    "section_fg": "#59636e",
    "header_bg": "#f3f4f6",
    "title_fg": "#1f2328",
    "sun_top": "#2563eb",
    "sun_mid": "#3b82f6",
    "sun_bottom": "#60a5fa",
    "grid": "#d0d7de",
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
    "accent2": "#38bdf8",
    "section_fg": "#a0a4ab",
    "header_bg": "#1e1f22",
    "title_fg": "#e6e6e6",
    "sun_top": "#5b8def",
    "sun_mid": "#7aa2ff",
    "sun_bottom": "#a9c4ff",
    "grid": "#3f4248",
}

# 80-as évek retró-futurisztikus éjszakai égbolt: neon magenta és cián, naplemente, rács
SYNTHWAVE = {
    "bg": "#0d0221",
    "surface": "#261447",
    "fg": "#f5e9ff",
    "muted": "#b8a6d9",
    "border": "#4d2a85",
    "accent": "#ff2a6d",
    "accent_fg": "#0d0221",
    "select_bg": "#3d1f6e",
    "piano_bg": "#120530",
    "key_white": "#efe8ff",
    "key_black": "#2a1153",
    "key_white_active": "#05d9e8",
    "key_black_active": "#ff2a6d",
    "key_outline": "#3a1d6b",
    "key_label": "#4b2c80",
    "log_bg": "#100427",
    "log_fg": "#d9c8ff",
    "accent2": "#05d9e8",
    "section_fg": "#05d9e8",
    "header_bg": "#0d0221",
    "title_fg": "#f5e9ff",
    "sun_top": "#fdd835",
    "sun_mid": "#ff9e00",
    "sun_bottom": "#ff2a6d",
    "grid": "#b026ff",
}

PALETTES = {SYNTHWAVE_MODE: SYNTHWAVE, LIGHT_MODE: LIGHT, DARK_MODE: DARK}


def palette_for(scheme: str) -> dict:
    """A 'synthwave' / 'light' / 'dark' sémához tartozó paletta (ismeretlen esetén a fallback)."""
    return PALETTES.get(scheme, PALETTES[FALLBACK_SCHEME])


def display_font(families) -> str:
    """Az első elérhető betűtípus a DISPLAY_FONTS listából (különben FONT_FAMILY)."""
    available = set(families)
    return next((f for f in DISPLAY_FONTS if f in available), FONT_FAMILY)


def _luminance(color: str) -> float:
    def channel(value: int) -> float:
        c = value / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(fg: str, bg: str) -> float:
    """WCAG kontrasztarány két #rrggbb szín között (1 … 21)."""
    hi, lo = sorted((_luminance(fg), _luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def mix(a: str, b: str, t: float) -> str:
    """Két #rrggbb szín keveréke (t = 0 → a, t = 1 → b)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


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
    """Mód ('synthwave'/'system'/'light'/'dark') -> konkrét séma ('synthwave'/'light'/'dark')."""
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
    """Mentett téma-mód; hiányzó / hibás fájl esetén az alapértelmezett (Synthwave)."""
    mode = load_setting("theme", DEFAULT_MODE, path)
    return mode if mode in MODES else DEFAULT_MODE


def save_mode(mode: str, path=None) -> bool:
    """Téma-mód mentése; True, ha sikerült."""
    if mode not in MODES:
        return False
    return save_setting("theme", mode, path)


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
