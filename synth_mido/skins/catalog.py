"""A skinek katalógusa: minden skin sötét és világos változattal.

Új skin: palettákat a `make_palette`-tel, fejléc rajzolót a `painters` modulba,
majd egy `register(Skin(...))` hívás ide.
"""

from synth_mido.skins import painters
from synth_mido.skins.palette import make_palette
from synth_mido.skins.registry import Skin, WidgetStyle, register

NEON = WidgetStyle(title_upper=True, button_edge="accent2", bold_buttons=True)

# Synthwave éjszaka: a TASK-009-ben egyeztetett tokenek, változatlanul
SYNTHWAVE_NIGHT = {
    "bg": "#0d0221", "surface": "#261447", "fg": "#f5e9ff", "muted": "#b8a6d9", "border": "#4d2a85",
    "accent": "#ff2a6d", "accent_fg": "#0d0221", "select_bg": "#3d1f6e", "piano_bg": "#120530",
    "key_white": "#efe8ff", "key_black": "#2a1153", "key_white_active": "#05d9e8", "key_black_active": "#ff2a6d",
    "key_outline": "#3a1d6b", "key_label": "#4b2c80", "log_bg": "#100427", "log_fg": "#d9c8ff",
    "accent2": "#05d9e8", "section_fg": "#05d9e8", "header_bg": "#0d0221", "title_fg": "#f5e9ff",
    "sun_top": "#fdd835", "sun_mid": "#ff9e00", "sun_bottom": "#ff2a6d", "grid": "#b026ff",
}

register(Skin(
    "synthwave", "Synthwave",
    dark=SYNTHWAVE_NIGHT,
    light=make_palette("#fdf0ff", "#ffffff", "#2b0f54", "#d1005b", "#007f8c", ("#ffb000", "#ff6a3d", "#d1005b"),
                       "#b026ff", key_black="#3a1660"),
    fonts=("Bahnschrift", "Segoe UI", "DejaVu Sans"), style=NEON, painter=painters.paint_synthwave,
))

register(Skin(
    "classic", "Klasszikus",
    dark=make_palette("#1e1f22", "#2b2d31", "#e6e6e6", "#5b8def", "#38bdf8", ("#5b8def", "#7aa2ff", "#a9c4ff"),
                      "#3f4248", piano_bg="#2b2b2b", key_white="#f5f5f5", key_black="#111111"),
    light=make_palette("#f3f4f6", "#ffffff", "#1f2328", "#2563eb", "#0ea5e9", ("#2563eb", "#3b82f6", "#60a5fa"),
                       "#d0d7de", piano_bg="#e5e7eb", key_white="#ffffff", key_black="#1f2937"),
    fonts=("Segoe UI", "DejaVu Sans"), painter=painters.paint_classic, header_height=34,
))

# --- 15 új skin -------------------------------------------------------------------

register(Skin(
    "astronaut", "Űrhajós",
    dark=make_palette("#070b1a", "#121a33", "#e8eefc", "#ff6b35", "#4cc9f0", ("#ffd166", "#ff9f1c", "#ff6b35"), "#3a4a7a"),
    light=make_palette("#eef3fb", "#ffffff", "#0b1530", "#e4572e", "#1d6fb8", ("#ffd166", "#ff9f1c", "#e4572e"), "#b8c6e0"),
    fonts=("Bahnschrift", "Segoe UI"), style=WidgetStyle(title_upper=True, button_edge="accent2"),
    painter=painters.paint_astronaut,
))
register(Skin(
    "safari", "Szafari",
    dark=make_palette("#1a120b", "#2a1d12", "#f6ead8", "#e07a1f", "#c9a227", ("#ffd27f", "#ff9a3c", "#d9480f"), "#5a3e22"),
    light=make_palette("#fbf3e4", "#fffaf0", "#2b1a0c", "#b4520a", "#6b8e23", ("#ffd27f", "#ff9a3c", "#d9480f"), "#d9c3a0"),
    fonts=("Constantia", "Georgia", "Segoe UI"), style=WidgetStyle(relief="raised", border_width=1),
    painter=painters.paint_safari,
))
register(Skin(
    "cartography", "Térkép",
    dark=make_palette("#0f1e24", "#17303a", "#e9f1ef", "#e9b44c", "#5fb3a1", ("#e9b44c", "#d98c3f", "#b5552b"), "#2f5560"),
    light=make_palette("#f4ecd8", "#fffaf0", "#2e2416", "#9c3d1f", "#2f6b5e", ("#e9b44c", "#d98c3f", "#9c3d1f"), "#c8b48a"),
    fonts=("Palatino Linotype", "Georgia", "Segoe UI"), style=WidgetStyle(frame_relief="groove"),
    painter=painters.paint_cartography,
))
register(Skin(
    "mathematics", "Matematika",
    dark=make_palette("#10241c", "#183528", "#eef6ee", "#f4d35e", "#8fd3ff", ("#f4d35e", "#ee964b", "#f95738"), "#2c5443"),
    light=make_palette("#f7fbff", "#ffffff", "#0d2238", "#d1495b", "#1f6feb", ("#f4d35e", "#ee964b", "#d1495b"), "#c9dcf2"),
    fonts=("Cambria", "Cambria Math", "Georgia"), style=WidgetStyle(button_padding=(10, 4)),
    painter=painters.paint_mathematics,
))
register(Skin(
    "antiquity", "Ókor",
    dark=make_palette("#1b1410", "#2a1f18", "#f3e6cf", "#c8922a", "#d4705f", ("#f0c75e", "#c8922a", "#8c5a1f"), "#4a3826"),
    light=make_palette("#f5ecd7", "#fffaf0", "#2b1d12", "#8c2f1f", "#7a5a12", ("#f0c75e", "#c8922a", "#8c5a1f"), "#d4c09a"),
    fonts=("Palatino Linotype", "Georgia"), style=WidgetStyle(relief="groove", border_width=2, frame_relief="groove"),
    painter=painters.paint_antiquity,
))
register(Skin(
    "ocean", "Óceán",
    dark=make_palette("#03172b", "#0a2742", "#e4f4ff", "#ff7f50", "#2ec4b6", ("#ffe8a3", "#ffb347", "#ff7f50"), "#12406b"),
    light=make_palette("#eaf8ff", "#ffffff", "#06243d", "#d94f30", "#0a7e8c", ("#ffe8a3", "#ffb347", "#d94f30"), "#b3dff0"),
    fonts=("Segoe UI", "DejaVu Sans"), painter=painters.paint_ocean,
))
register(Skin(
    "forest", "Erdő",
    dark=make_palette("#0d1a12", "#14281c", "#e8f3e8", "#d4a017", "#6fcf97", ("#f2e394", "#d4a017", "#8a5a00"), "#24432f"),
    light=make_palette("#f1f7ee", "#ffffff", "#13261a", "#a0522d", "#2e7d32", ("#f2e394", "#d4a017", "#a0522d"), "#c7dcc4"),
    fonts=("Candara", "Segoe UI"), painter=painters.paint_forest,
))
register(Skin(
    "sakura", "Szakura",
    dark=make_palette("#1a0f1a", "#2a1828", "#fbeef5", "#ff8fb1", "#c3a6ff", ("#ffd1dc", "#ff8fb1", "#e0457b"), "#4a2a44"),
    light=make_palette("#fff4f8", "#ffffff", "#3a1027", "#c2185b", "#7b1fa2", ("#ffd1dc", "#ff8fb1", "#c2185b"), "#f2c6d6"),
    fonts=("Yu Gothic UI", "Segoe UI"), painter=painters.paint_sakura,
))
register(Skin(
    "steampunk", "Steampunk",
    dark=make_palette("#17110b", "#261b11", "#f1e3c8", "#c08a3e", "#cf7a32", ("#e6c07b", "#c08a3e", "#7a4a1c"), "#4a3622"),
    light=make_palette("#f3e9d6", "#fbf5ea", "#2a1c0f", "#8a5a1c", "#6d3b12", ("#e6c07b", "#c08a3e", "#7a4a1c"), "#d1bd98"),
    fonts=("Constantia", "Georgia", "Segoe UI"),
    style=WidgetStyle(title_upper=True, relief="ridge", border_width=2, frame_relief="ridge", button_edge="accent"),
    painter=painters.paint_steampunk,
))
register(Skin(
    "arcade", "Arcade",
    dark=make_palette("#0a0a12", "#15152a", "#f0f0ff", "#ff3864", "#2de2e6", ("#fffb96", "#ff9e00", "#ff3864"), "#3b2c7a"),
    light=make_palette("#f5f5ff", "#ffffff", "#12122a", "#d6004c", "#0077b6", ("#fffb96", "#ff9e00", "#d6004c"), "#c9c9ef"),
    fonts=("Consolas", "Courier New", "DejaVu Sans Mono"),
    style=WidgetStyle(title_upper=True, button_padding=(10, 4), border_width=2, button_edge="accent2", bold_buttons=True),
    painter=painters.paint_arcade,
))
register(Skin(
    "artdeco", "Art Deco",
    dark=make_palette("#0b0b0b", "#1a1a1a", "#f5efe0", "#d4af37", "#2f9e8f", ("#f7e7a1", "#d4af37", "#9c7a1b"), "#3d3420"),
    light=make_palette("#f8f4ea", "#ffffff", "#1a1a1a", "#8c6d1f", "#1f6f66", ("#f7e7a1", "#d4af37", "#8c6d1f"), "#d9cfb0"),
    fonts=("Bahnschrift", "Century Gothic", "Segoe UI"),
    style=WidgetStyle(title_upper=True, button_padding=(14, 6), border_width=2, button_edge="accent"),
    painter=painters.paint_artdeco,
))
register(Skin(
    "desert", "Sivatag",
    dark=make_palette("#1d1020", "#2c1a2e", "#fbeee0", "#f08a4b", "#f2c14e", ("#ffe29a", "#f08a4b", "#c8553d"), "#4a2c3a"),
    light=make_palette("#fff6e8", "#ffffff", "#3a2210", "#b4471f", "#8a6d0b", ("#ffe29a", "#f08a4b", "#c8553d"), "#e8cfa8"),
    fonts=("Candara", "Segoe UI"), painter=painters.paint_desert,
))
register(Skin(
    "arctic", "Sarkvidék",
    dark=make_palette("#06121e", "#0e2233", "#eaf6ff", "#7cf5c3", "#a78bfa", ("#c1fbe4", "#7cf5c3", "#a78bfa"), "#1b3a52"),
    light=make_palette("#f2f8fc", "#ffffff", "#0b2236", "#0f766e", "#4f46e5", ("#c1fbe4", "#7cf5c3", "#4f46e5"), "#c8dceb"),
    fonts=("Segoe UI", "DejaVu Sans"), painter=painters.paint_arctic,
))
register(Skin(
    "volcano", "Vulkán",
    dark=make_palette("#140606", "#241010", "#fde8e0", "#ff4d00", "#ffb703", ("#ffd166", "#ff7b00", "#d00000"), "#4a1a12"),
    light=make_palette("#fdf1ec", "#ffffff", "#2a0d06", "#c1121f", "#b45309", ("#ffd166", "#ff7b00", "#c1121f"), "#f0c9b8"),
    fonts=("Bahnschrift", "Segoe UI"), style=WidgetStyle(title_upper=True, button_edge="accent"),
    painter=painters.paint_volcano,
))
register(Skin(
    "jazz", "Jazz klub",
    dark=make_palette("#0d0a14", "#1b1526", "#f4eee4", "#e0a43a", "#d96a8a", ("#f6d08b", "#e0a43a", "#c44569"), "#33283f"),
    light=make_palette("#f7f1e8", "#ffffff", "#1f1428", "#8e2c48", "#8a5a0b", ("#f6d08b", "#e0a43a", "#8e2c48"), "#ddd0bc"),
    fonts=("Constantia", "Georgia", "Segoe UI"), style=WidgetStyle(relief="raised"),
    painter=painters.paint_jazz,
))
