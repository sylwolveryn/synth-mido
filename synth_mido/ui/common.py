"""A felület közös állandói és segédfüggvényei."""


from synth_mido.skins import theme

C_MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71, 72]
C_MAJOR_CHORD = [60, 64, 67]
DEMO_MELODY = [
    76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 68, 71, 72, 64,
    76, 75, 76, 75, 76, 71, 74, 72, 69,
]
PIANO_HEIGHT = 150


def pretty_instrument(name: str) -> str:
    return name.replace("_", " ").title()


def format_seconds(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def speed_label(speed: float) -> str:
    return f"{speed:g}x"


THEME_LABELS = {
    theme.SYNTHWAVE_MODE: "Synthwave",
    theme.SYSTEM_MODE: "Rendszer",
    theme.LIGHT_MODE: "Világos",
    theme.DARK_MODE: "Sötét",
}
THEME_POLL_MS = 2000
HEADER_HEIGHT = 92        # Synthwave fejléc
HEADER_HEIGHT_PLAIN = 34  # egyszerű címsor a többi témában
RECORD_TICK_MS = 250
PLAYER_TICK_MS = 100
FX_HEIGHT = 96      # px — a hangvizualizáció sávja a zongora fölött
FX_FRAME_MS = 33    # ~30 képkocka / mp
SEEK_MARGIN = 8  # px — a csúszka két végén a fogantyú fele
