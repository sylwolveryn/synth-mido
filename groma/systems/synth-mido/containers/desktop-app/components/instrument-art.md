---
type: C4 Component
title: Instrument illustrations
status: stable
groma:
  id: instrument-art
  parent: desktop-app
  code:
    - scanner: python
      file: synth_mido/fx/instrument_art.py
  technology: Python
  group: Visual effects
description: A cute animal playing the instrument of each General MIDI family
---

16 families (program // 8) map to 16 pre-designed animal + instrument scenes (cat at the piano, bird with a flute, elephant with a trumpet, ...). Scenes are drawn from canvas primitives in a 100 x 100 unit box with a small pen helper, coloured from the skin palette; any object with Tk canvas create methods works, so the model is testable without a window.
