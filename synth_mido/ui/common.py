"""A felület közös állandói és segédfüggvényei."""

PIANO_HEIGHT = 150


def pretty_instrument(name: str) -> str:
    return name.replace("_", " ").title()


def format_seconds(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def speed_label(speed: float) -> str:
    return f"{speed:g}x"


THEME_POLL_MS = 2000
HEADER_HEIGHT = 92  # a skin fejléc alapmagassága (a skin felülírhatja)
RECORD_TICK_MS = 250
PLAYER_TICK_MS = 100
FX_HEIGHT = 96      # px — a hangvizualizáció sávja a zongora fölött
FX_FRAME_MS = 33    # ~30 képkocka / mp
SEEK_MARGIN = 8  # px — a csúszka két végén a fogantyú fele
