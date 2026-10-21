"""Hangszer illusztráció a Lejátszás részben: a választott hangszercsalád állata a hangszerével."""

from synth_mido import config
from synth_mido.core.i18n import t
from synth_mido.fx import instrument_art
from synth_mido.ui.common import ART_SIZE, pretty_instrument

class InstrumentArtMixin:

    def _selected_program(self) -> int:
        label = self.instrument_var.get()
        for name, program in config.INSTRUMENTS.items():
            if pretty_instrument(name) == label:
                return program
        return 0


    def draw_instrument_art(self):
        """Az illusztráció újrarajzolása (hangszer- vagy skinváltáskor, átméretezéskor)."""
        c, p = self.art_canvas, self.palette
        c.delete("all")
        c.configure(bg=p["bg"])
        width = max(c.winfo_width(), ART_SIZE + 40)
        x = width - ART_SIZE - 4
        family = instrument_art.paint(c, self._selected_program(), x, 0, ART_SIZE - 4, p)
        c.create_text(x - 8, ART_SIZE * 0.42, anchor="e", text=t(f"art.{family.id}"), fill=p["fg"],
                      font=(self.font_family, 10, "bold"), tags=("caption",))
        c.create_text(x - 8, ART_SIZE * 0.42 + 18, anchor="e", text=self.instrument_var.get(), fill=p["muted"],
                      font=(self.font_family, 9), tags=("caption",))
