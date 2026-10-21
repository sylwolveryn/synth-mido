"""A daloskönyv felvételeinek (újra)generálása a records/ mappába.

Futtatás a projekt gyökeréből:  python -m scripts.build_songbook
"""

from synth_mido.core import songbook


def main():
    for path in songbook.write_all():
        print(f"✓ {path.name}")
    print(f"{len(songbook.SONGS)} dal a records/ mappában.")


if __name__ == "__main__":
    main()
