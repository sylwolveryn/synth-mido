"""Daloskönyv: közismert, közkincs (public domain) zeneművek felvételként.

Csak szerzői jogi védelem alatt nem álló művek (a szerző több mint 70 éve hunyt
el, vagy népdal). Modern, védett művek (pl. az Imperial March, John Williams 1980)
szándékosan nincsenek benne.

Jelölés (negyedhang = 1 ütés):
    "E5:0.5"        hang:hossz       (C4 = 60, # és b is lehet: F#4, Bb3, E#4)
    "C4+E4+G4:2"    akkord
    "R:1"           szünet
    "|"             ütemvonal (csak olvashatóság)
Egy dal szakaszokból áll; egy szakasz szólamai egyszerre indulnak, a következő
szakasz a leghosszabb szólam végén kezdődik.
"""

from dataclasses import dataclass
from typing import List, Sequence, Tuple

from synth_mido.config import INSTRUMENTS
from synth_mido.core import recorder

NOTE_INDEX = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
LEGATO = 0.9          # a hang a hossz ennyi részéig szól
CREATED = "2026-10-21T00:00:00"


def parse_pitch(text: str) -> int:
    """'C4' → 60, 'F#4' → 66, 'Bb3' → 58, 'E#4' → 65."""
    name, rest = text[0].upper(), text[1:]
    shift = 0
    while rest and rest[0] in "#b":
        shift += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + NOTE_INDEX[name] + shift


def parse_voice(tokens: str) -> List[Tuple[Tuple[int, ...], float]]:
    """'E5:0.5 R:1 C4+E4:2' → [((76,), 0.5), ((), 1.0), ((60, 64), 2.0)]."""
    out = []
    for tok in tokens.split():
        if tok == "|":
            continue
        pitches, _, dur = tok.partition(":")
        beats = float(dur) if dur else 1.0
        notes = () if pitches.upper() == "R" else tuple(parse_pitch(p) for p in pitches.split("+"))
        out.append((notes, beats))
    return out


def voice_beats(tokens: str) -> float:
    return sum(beats for _, beats in parse_voice(tokens))


@dataclass(frozen=True)
class Section:
    bpm: float
    voices: Sequence[Tuple[int, str]]   # (hangerő, jelölés)


@dataclass(frozen=True)
class Song:
    name: str
    composer: str
    year: str
    instrument: str
    sections: Sequence[Section]

    def to_record(self) -> dict:
        notes, start = [], 0.0
        for section in self.sections:
            spb = 60.0 / section.bpm
            longest = 0.0
            for velocity, tokens in section.voices:
                t = 0.0
                for pitches, beats in parse_voice(tokens):
                    for p in pitches:
                        notes.append({
                            "note": p, "velocity": velocity,
                            "start": round(start + t * spb, 3), "duration": round(beats * spb * LEGATO, 3),
                        })
                    t += beats
                longest = max(longest, t)
            start += longest * spb
        notes.sort(key=lambda n: (n["start"], n["note"]))
        return {
            "format": recorder.FORMAT,
            "version": recorder.VERSION,
            "created": CREATED,
            "instrument": {"name": self.instrument, "program": INSTRUMENTS[self.instrument]},
            "duration": round(start, 3),
            "notes": notes,
        }


def rep(text: str, times: int) -> str:
    return " ".join([text] * times)


# --- a dalok ---------------------------------------------------------------------------

# Für Elise — A rész, első és második befejezés, epizód, visszatérés
_FE_A1 = "E5:.25 D#5:.25 E5:.25 B4:.25 D5:.25 C5:.25 | A4:.5 R:.25 C4:.25 E4:.25 A4:.25 | " \
         "B4:.5 R:.25 E4:.25 G#4:.25 B4:.25 | C5:.5 R:.25 E4:.25 E5:.25 D#5:.25"
_FE_A2 = "E5:.25 D#5:.25 E5:.25 B4:.25 D5:.25 C5:.25 | A4:.5 R:.25 C4:.25 E4:.25 A4:.25 | " \
         "B4:.5 R:.25 E4:.25 C5:.25 B4:.25"
_FE_L1 = "R:1.5 | A2:.25 E3:.25 A3:.25 R:.75 | E2:.25 E3:.25 G#3:.25 R:.75 | A2:.25 E3:.25 A3:.25 R:.75"
_FE_L2 = "R:1.5 | A2:.25 E3:.25 A3:.25 R:.75 | E2:.25 E3:.25 G#3:.25 R:.75"
FUR_ELISE = Song("Für Elise", "Ludwig van Beethoven", "1810", "acoustic_grand_piano", [
    Section(72, [(80, "E5:.25 D#5:.25"), (60, "R:.5")]),
    Section(72, [(80, _FE_A1), (62, _FE_L1)]),
    Section(72, [(80, _FE_A2 + " | A4:.5 R:.5 E5:.25 D#5:.25"), (62, _FE_L2 + " | A2:.25 E3:.25 A3:.25 R:.75")]),
    Section(72, [(80, _FE_A1), (62, _FE_L1)]),
    Section(72, [(80, _FE_A2 + " | A4:.5 R:.25 B4:.25 C5:.25 D5:.25 | E5:.75 G4:.25 F5:.25 E5:.25 | "
                      "D5:.75 F4:.25 E5:.25 D5:.25 | C5:.75 E4:.25 D5:.25 C5:.25 | B4:.5 R:.25 E4:.25 E5:.25 D#5:.25"),
                 (62, _FE_L2 + " | A2:.25 E3:.25 A3:.25 R:.75 | C3:.25 G3:.25 C4:.25 R:.75 | "
                      "G2:.25 G3:.25 B3:.25 R:.75 | A2:.25 E3:.25 A3:.25 R:.75 | E2:.25 E3:.25 E4:.25 R:.75")]),
    Section(72, [(80, _FE_A1), (62, _FE_L1)]),
    Section(72, [(80, _FE_A2 + " | A4:1.5"), (62, _FE_L2 + " | A2:.25 E3:.25 A3:1")]),
])

ODE_TO_JOY = Song("Ode to Joy", "Ludwig van Beethoven", "1824", "string_ensemble_1", [
    Section(112, [
        (90, "E4 E4 F4 G4 | G4 F4 E4 D4 | C4 C4 D4 E4 | E4:1.5 D4:.5 D4:2 | "
             "E4 E4 F4 G4 | G4 F4 E4 D4 | C4 C4 D4 E4 | D4:1.5 C4:.5 C4:2 | "
             "D4 D4 E4 C4 | D4 E4:.5 F4:.5 E4 C4 | D4 E4:.5 F4:.5 E4 D4 | C4 D4 G3:2 | "
             "E4 E4 F4 G4 | G4 F4 E4 D4 | C4 C4 D4 E4 | D4:1.5 C4:.5 C4:2"),
        (60, "C3+G3:4 | G2+D3:4 | C3+G3:4 | G2+D3:2 G2+B2:2 | C3+G3:4 | G2+D3:4 | C3+G3:4 | G2+D3:2 C3+G3:2 | "
             "G2+D3:4 | C3+G3:2 G2+D3:2 | C3+G3:2 G2+D3:2 | C3+E3:2 G2+B2:2 | "
             "C3+G3:4 | G2+D3:4 | C3+G3:4 | G2+D3:2 C3+G3:2"),
    ]),
])

TWINKLE = Song("Twinkle Twinkle Little Star", "népdal (Mozart variációk)", "1761", "music_box", [
    Section(100, [
        (85, "C4 C4 G4 G4 | A4 A4 G4:2 | F4 F4 E4 E4 | D4 D4 C4:2 | G4 G4 F4 F4 | E4 E4 D4:2 | "
             "G4 G4 F4 F4 | E4 E4 D4:2 | C4 C4 G4 G4 | A4 A4 G4:2 | F4 F4 E4 E4 | D4 D4 C4:2"),
        (55, "C3:2 E3:2 | F3:2 E3:2 | D3:2 C3:2 | G2:2 C3:2 | E3:2 D3:2 | C3:2 G2:2 | "
             "E3:2 D3:2 | C3:2 G2:2 | C3:2 E3:2 | F3:2 E3:2 | D3:2 C3:2 | G2:2 C3:2"),
    ]),
])

RONDO_ALLA_TURCA = Song("Rondo alla Turca", "Wolfgang Amadeus Mozart", "1783", "acoustic_grand_piano", [
    Section(126, [(85, "B4:.25 A4:.25 G#4:.25 A4:.25"), (60, "R:1")]),
    Section(126, [
        (85, "C5:.5 R:.5 D5:.25 C5:.25 B4:.25 C5:.25 | E5:.5 R:.5 F5:.25 E5:.25 D#5:.25 E5:.25 | "
             "B5:.25 A5:.25 G#5:.25 A5:.25 B5:.25 A5:.25 G#5:.25 A5:.25 | C6:1 A5:.5 C6:.5 | "
             "B5:.5 A5:.5 G5:.5 A5:.5 | B5:.5 A5:.5 G5:.5 A5:.5 | B5:.5 A5:.5 G5:.5 F#5:.5 | E5:1 "
             "B4:.25 A4:.25 G#4:.25 A4:.25 | C5:.5 R:.5 D5:.25 C5:.25 B4:.25 C5:.25 | "
             "E5:.5 R:.5 F5:.25 E5:.25 D#5:.25 E5:.25 | B5:.25 A5:.25 G#5:.25 A5:.25 B5:.25 A5:.25 G#5:.25 A5:.25 | "
             "C6:1 A5:.5 B5:.5 | C6:.5 B5:.5 A5:.5 G#5:.5 | A5:.5 E5:.5 F5:.5 D5:.5 | C5:1 B4:.5 A4:.5 | A4:2"),
        (60, "A2:.5 C4+E4:.5 C4+E4:.5 C4+E4:.5 | A2:.5 C4+E4:.5 C4+E4:.5 C4+E4:.5 | A2:.5 C4+E4:.5 C4+E4:.5 C4+E4:.5 | "
             "A2:.5 C4+E4:.5 A2:.5 C4+E4:.5 | E2:.5 B3+E4:.5 E2:.5 B3+E4:.5 | A2:.5 C4+E4:.5 A2:.5 C4+E4:.5 | "
             "E2:.5 B3+E4:.5 E2:.5 B3+D4:.5 | E2:.5 G#3+D4:.5 R:1 | A2:.5 C4+E4:.5 C4+E4:.5 C4+E4:.5 | "
             "A2:.5 C4+E4:.5 C4+E4:.5 C4+E4:.5 | A2:.5 C4+E4:.5 C4+E4:.5 C4+E4:.5 | A2:.5 C4+E4:.5 A2:.5 C4+E4:.5 | "
             "A2:.5 C4+E4:.5 E2:.5 B3+E4:.5 | F2:.5 A3+D4:.5 D2:.5 F3+A3:.5 | E2:.5 A3+C4:.5 E2:.5 G#3+B3:.5 | A2+A3:2"),
    ]),
])

_MK_THEME = "B3:.5 C#4:.5 D4:.5 E4:.5 F#4:.5 D4:.5 F#4:1 | F4:.5 C#4:.5 F4:1 E4:.5 C4:.5 E4:1 | " \
            "B3:.5 C#4:.5 D4:.5 E4:.5 F#4:.5 D4:.5 F#4:.5 B4:.5 | A4:.5 F#4:.5 D4:.5 F#4:.5 A4:2"
_MK_BASS = "B1+F#2:1 R:1 B1+F#2:1 R:1 | C#2+G#2:1 R:1 C2+G2:1 R:1 | B1+F#2:1 R:1 B1+F#2:1 R:1 | D2+A2:1 R:1 D2+A2:2"
MOUNTAIN_KING = Song("In the Hall of the Mountain King", "Edvard Grieg", "1875", "pizzicato_strings", [
    Section(bpm, [(vel, _MK_THEME), (vel - 25, _MK_BASS)])
    for bpm, vel in ((100, 60), (125, 75), (155, 90), (190, 105), (230, 120))
])

_CANON_BASS = "D3:2 A2:2 | B2:2 F#2:2 | G2:2 D2:2 | G2:2 A2:2"
_CANON_PADS = "F#3+A3:2 E3+A3:2 | D3+F#3:2 C#3+F#3:2 | B2+D3:2 A2+D3:2 | B2+D3:2 C#3+E3:2"
CANON_IN_D = Song("Canon in D", "Johann Pachelbel", "1680", "string_ensemble_1", [
    Section(66, [(70, _CANON_BASS), (45, _CANON_PADS)]),
    Section(66, [(85, "F#5:2 E5:2 | D5:2 C#5:2 | B4:2 A4:2 | B4:2 C#5:2"), (70, _CANON_BASS), (45, _CANON_PADS)]),
    Section(66, [(85, "D5:2 C#5:2 | B4:2 A4:2 | G4:2 F#4:2 | G4:2 E4:2"), (70, _CANON_BASS), (45, _CANON_PADS)]),
    Section(66, [(85, "D4 F#4 A4 G4 | F#4 D4 F#4 E4 | D4 B3 D4 A4 | G4 B4 A4 G4"), (70, _CANON_BASS),
                 (45, _CANON_PADS)]),
    Section(66, [(85, "F#4 D4 E4 C#5 | D5 F#5 A5 A4 | B4 G4 A4 F#4 | D4 D5 D5:1.5 C#5:.5"), (70, _CANON_BASS),
                 (45, _CANON_PADS)]),
    Section(66, [(85, "D5:4"), (70, "D3:4"), (45, "F#3+A3:4")]),
])

FUNERAL_MARCH = Song("Funeral March", "Frédéric Chopin", "1839", "acoustic_grand_piano", [
    Section(52, [
        (80, rep("Bb3:1 Bb3:.75 Bb3:.25 Bb3:2 | Db4:.75 C4:.25 C4:.75 Bb3:.25 Bb3:.75 A3:.25 Bb3:1", 2)),
        (55, rep("Bb1+F2:1 Gb2+Db3:1 Bb1+F2:1 Gb2+Db3:1 | Bb1+F2:1 Gb2+Db3:1 Bb1+F2:1 Gb2+Db3:1", 2)),
    ]),
    Section(52, [(70, "Bb3+F4:4"), (55, "Bb1+F2:4")]),
])

_WT = "G4:.25 G4:.25 G4:.5"
WILLIAM_TELL = Song("William Tell Overture - Finale", "Gioachino Rossini", "1829", "brass_section", [
    Section(152, [
        (95, f"{_WT} {_WT} | G4:.25 G4:.25 C5:.5 D5:.5 E5:.5 | {_WT} {_WT} | G4:.25 G4:.25 C5:.5 E5:.5 D5:.5 | "
             f"B4:.5 G4:1.5 | {_WT} {_WT} | G4:.25 G4:.25 C5:.5 D5:.5 E5:.5 | C5:.5 E5:.5 G5:1 | "
             "F5:.5 E5:.5 D5:.5 C5:.5 | E5:.5 C5:.5 C5:1"),
        (65, "C3:.5 G3:.5 C3:.5 G3:.5 | C3:.5 G3:.5 C3:.5 G3:.5 | C3:.5 G3:.5 C3:.5 G3:.5 | G2:.5 D3:.5 G2:.5 D3:.5 | "
             "G2:.5 D3:.5 G2:.5 B2:.5 | C3:.5 G3:.5 C3:.5 G3:.5 | C3:.5 G3:.5 C3:.5 G3:.5 | C3:.5 E3:.5 G3:1 | "
             "G2:.5 B2:.5 D3:.5 G2:.5 | C3:.5 G2:.5 C3:1"),
    ]),
])

MINUET_IN_G = Song("Minuet in G", "Christian Petzold", "1725", "harpsichord", [
    Section(120, [
        (85, "D5 G4:.5 A4:.5 B4:.5 C5:.5 | D5 G4 G4 | E5 C5:.5 D5:.5 E5:.5 F#5:.5 | G5 G4 G4 | "
             "C5 D5:.5 C5:.5 B4:.5 A4:.5 | B4 C5:.5 B4:.5 A4:.5 G4:.5 | F#4 G4:.5 A4:.5 B4:.5 G4:.5 | A4:3 | "
             "D5 G4:.5 A4:.5 B4:.5 C5:.5 | D5 G4 G4 | E5 C5:.5 D5:.5 E5:.5 F#5:.5 | G5 G4 G4 | "
             "C5 D5:.5 C5:.5 B4:.5 A4:.5 | B4 C5:.5 B4:.5 A4:.5 G4:.5 | A4 B4:.5 A4:.5 G4:.5 F#4:.5 | G4:3"),
        (60, "G3+B3:2 A3 | B3:3 | C4:3 | B3:3 | A3:3 | G3:3 | D4 B3 G3 | D4 D3 C4 | "
             "B2+G3:2 A3 | B3:3 | C4:3 | B3:3 | A3:3 | G3:3 | D4 D3 F#3 | G3 G2:2"),
    ]),
])

MORNING_MOOD = Song("Morning Mood", "Edvard Grieg", "1875", "flute", [
    Section(84, [
        (80, "G5:.5 E5:.5 D5:.5 C5:.5 D5:.5 E5:.5 | G5:.5 E5:.5 D5:.5 C5:.5 D5:.5 E5:.25 D5:.25 | "
             "E5:.5 G5:.5 E5:.5 G5:.5 A5:.5 E5:.5 | A5:.5 G5:.5 E5:.5 D5:1.5 | "
             "G5:.5 E5:.5 D5:.5 C5:.5 D5:.5 E5:.5 | G5:.5 E5:.5 D5:.5 C5:.5 D5:.5 E5:.25 D5:.25 | "
             "E5:.5 G5:.5 E5:.5 G5:.5 A5:.5 E5:.5 | A5:.5 G5:.5 E5:.5 C5:1.5"),
        (50, "C3+G3:3 | C3+G3:3 | C3+A3:3 | F3+A3:1.5 G3+B3:1.5 | C3+G3:3 | C3+G3:3 | A2+E3:3 | F2+C3:1.5 C3+G3:1.5"),
    ]),
])

BRAHMS_LULLABY = Song("Brahms Lullaby", "Johannes Brahms", "1868", "music_box", [
    Section(96, [
        (75, "R:2 E4:.5 E4:.5 | G4:2 E4:.5 E4:.5 | G4:2 E4:.5 G4:.5 | C5 B4:1.5 A4:.5 | A4 G4 D4:.5 E4:.5 | "
             "F4 D4 D4:.5 E4:.5 | F4:2 D4:.5 F4:.5 | B4:.5 A4:.5 G4 B4 | C5:2"),
        (45, "R:3 | C3+G3:3 | C3+G3:3 | C3+E3:3 | C3+E3:3 | G2+D3:3 | G2+D3:3 | G2+F3:3 | C3+E3:2"),
    ]),
])

JINGLE_BELLS = Song("Jingle Bells", "James Lord Pierpont", "1857", "acoustic_grand_piano", [
    Section(132, [
        (85, "E4 E4 E4:2 | E4 E4 E4:2 | E4 G4 C4:1.5 D4:.5 | E4:4 | F4 F4 F4:1.5 F4:.5 | F4 E4 E4 E4:.5 E4:.5 | "
             "E4 D4 D4 E4 | D4:2 G4:2 | E4 E4 E4:2 | E4 E4 E4:2 | E4 G4 C4:1.5 D4:.5 | E4:4 | "
             "F4 F4 F4:1.5 F4:.5 | F4 E4 E4 E4:.5 E4:.5 | G4 G4 F4 D4 | C4:4"),
        (55, "C3:2 G2:2 | C3:2 G2:2 | C3:2 G2:2 | C3:2 E3:2 | F2:2 C3:2 | C3:2 G2:2 | D3:2 A2:2 | G2:2 B2:2 | "
             "C3:2 G2:2 | C3:2 G2:2 | C3:2 G2:2 | C3:2 E3:2 | F2:2 C3:2 | C3:2 G2:2 | G2:2 B2:2 | C3:4"),
    ]),
])

GREENSLEEVES = Song("Greensleeves", "népdal (angol)", "1580", "acoustic_guitar_nylon", [
    Section(150, [
        (80, "A4 | C5:2 D5 | E5:1.5 F5:.5 E5 | D5:2 B4 | G4:1.5 A4:.5 B4 | C5:2 A4 | A4:1.5 G#4:.5 A4 | B4:2 G#4 | E4:2 A4 | "
             "C5:2 D5 | E5:1.5 F5:.5 E5 | D5:2 B4 | G4:1.5 A4:.5 B4 | C5:1.5 B4:.5 A4 | G#4:1.5 F#4:.5 G#4 | A4:3 | A4:2"),
        (50, "R | A2+E3:3 | C3+G3:3 | G2+D3:3 | E2+B2:3 | A2+E3:3 | F2+C3:3 | E2+B2:3 | E2+B2:3 | "
             "A2+E3:3 | C3+G3:3 | G2+D3:3 | E2+B2:3 | A2+E3:3 | E2+B2:3 | A2+E3:3 | A2+E3:2"),
    ]),
])

EINE_KLEINE = Song("Eine kleine Nachtmusik", "Wolfgang Amadeus Mozart", "1787", "string_ensemble_1", [
    Section(132, [
        (90, "G4:1 R:.5 D4:.5 G4:1 R:.5 D4:.5 | G4:.5 D4:.5 G4:.5 B4:.5 D5:2 | "
             "C5:1 R:.5 A4:.5 C5:1 R:.5 A4:.5 | C5:.5 A4:.5 F#4:.5 A4:.5 D4:2 | "
             "G4:2 G4:1.5 B4:.5 | A4:.5 G4:.5 G4:.5 F#4:.5 F#4:2 | "
             "A4:1.5 C5:.5 F#4:.5 A4:.5 G4:.5 F#4:.5 | E4:.5 G4:.5 F#4:.5 A4:.5 G4:2"),
        (60, "G2+G3:1 R:1 G2+G3:1 R:1 | G2+G3:1 R:1 G2+B2:2 | D3+D4:1 R:1 D3+D4:1 R:1 | D3:1 R:1 D2+D3:2 | "
             "G2+B2:2 G2+B2:2 | D3+F#3:2 D3+A3:2 | D3+F#3:2 D3+C4:2 | C3+E3:1 D3:1 G2+G3:2"),
    ]),
])

THE_ENTERTAINER = Song("The Entertainer", "Scott Joplin", "1902", "honky_tonk_piano", [
    Section(92, [
        (85, "D5:.25 D#5:.25 | E5:.25 C6:.5 E5:.25 C6:.5 E5:.25 C6:.25 | C6:1.5 C6:.25 D6:.25 | "
             "D#6:.25 E6:.25 C6:.25 D6:.25 E6:.5 B5:.25 D6:.25 | C6:1.5 D5:.25 D#5:.25 | "
             "E5:.25 C6:.5 E5:.25 C6:.5 E5:.25 C6:.25 | C6:1.5 A5:.25 G5:.25 | "
             "F#5:.25 A5:.25 C6:.25 E6:.5 D6:.25 C6:.25 A5:.25 | D6:2"),
        (60, "R:.5 | C3:.5 C3+E3+G3:.5 G2:.5 C3+E3+G3:.5 | C3:.5 C3+E3+G3:.5 E3:.5 C3+E3+G3:.5 | "
             "G2:.5 F3+G3+B3:.5 D3:.5 F3+G3+B3:.5 | C3:.5 C3+E3+G3:.5 R:1 | "
             "C3:.5 C3+E3+G3:.5 G2:.5 C3+E3+G3:.5 | C3:.5 C3+E3+G3:.5 A2:.5 C3+F#3+A3:.5 | "
             "D3:.5 C3+F#3+A3:.5 D3:.5 C3+F#3+A3:.5 | G2+D3+G3:2"),
    ]),
])

GYMNOPEDIE = Song("Gymnopédie No. 1", "Erik Satie", "1888", "electric_piano_1", [
    Section(72, [
        (35, rep("G2:1 B3+D4+F#4:2 | D2:1 A3+C#4+F#4:2", 2)),
    ]),
    Section(72, [
        (70, "R:1 F#5:1 A5:1 | G5:1 F#5:1 C#5:1 | B4:1 C#5:1 D5:1 | A4:3 | F#4:3 | R:3"),
        (35, rep("G2:1 B3+D4+F#4:2 | D2:1 A3+C#4+F#4:2", 3)),
    ]),
])

TOCCATA = Song("Toccata and Fugue in D minor", "Johann Sebastian Bach", "1705", "church_organ", [
    Section(60, [(90, "A5:.125 G5:.125 A5:2.75 | G5:.25 F5:.25 E5:.25 D5:.25 C#5:1 D5:2 | R:.5")]),
    Section(60, [(90, "A4:.125 G4:.125 A4:2.75 | E4:.5 F4:.5 C#4:1 D4:2 | R:.5")]),
    Section(60, [(85, "A3:.125 G3:.125 A3:2.75 | G3:.25 F3:.25 E3:.25 D3:.25 C#3:1 D3:2"),
                 (70, "R:3 | R:2 D2+A2:2")]),
    Section(60, [(95, "C#3+E3+G3+A#3+C#4+E4:2 | D3+F3+A3+D4+F4:3"), (75, "D2:2 | D1+D2:3")]),
])

MOONLIGHT = Song("Moonlight Sonata", "Ludwig van Beethoven", "1801", "acoustic_grand_piano", [
    Section(54, [
        (55, rep("G#3:.333 C#4:.333 E4:.334", 4) + " | " + rep("G#3:.333 C#4:.333 E4:.334", 4) + " | "
             + rep("A3:.333 C#4:.333 E4:.334", 2) + " " + rep("A3:.333 D4:.333 F#4:.334", 2) + " | "
             + "G#3:.333 C4:.333 F#4:.334 G#3:.333 C#4:.333 E4:.334 G#3:.333 C#4:.333 D#4:.334 "
             + "F#3:.333 C4:.333 D#4:.334 | " + rep("E3:.333 G#3:.333 C#4:.334", 4)),
        (50, "C#2+C#3:4 | B1+B2:4 | A1+A2:2 F#1+F#2:2 | G#1+G#2:4 | C#2+C#3:4"),
    ]),
])

SONGS: Tuple[Song, ...] = (
    FUR_ELISE, ODE_TO_JOY, TWINKLE, RONDO_ALLA_TURCA, MOUNTAIN_KING, CANON_IN_D, FUNERAL_MARCH, WILLIAM_TELL,
    MINUET_IN_G, MORNING_MOOD, BRAHMS_LULLABY, JINGLE_BELLS, GREENSLEEVES, EINE_KLEINE, THE_ENTERTAINER,
    GYMNOPEDIE, TOCCATA, MOONLIGHT,
)


def write_all(directory=None) -> List:
    """Az összes dal felvételként a records/ mappába (felülírja a korábbi változatot)."""
    return [recorder.save_record(song.to_record(), song.name, directory, overwrite=True) for song in SONGS]
