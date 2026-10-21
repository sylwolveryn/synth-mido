"""Hangvizualizáció sáv a zongora fölött."""

import time

from synth_mido.core import piano_layout
from synth_mido.skins import theme
from synth_mido.ui.common import (
    FX_FRAME_MS,
    FX_HEIGHT,
    PIANO_HEIGHT,
)


class FxMixin:

    def _fx_key_span(self, note: int):
        key = self._fx_keys.get(note)
        return (key.x0, key.x1, key.black) if key else None


    def draw_fx_floor(self):
        """Az effekt sáv statikus háttere: halvány perspektivikus rács (Synthwave-ben neon)."""
        c, p = self.fx_canvas, self.palette
        width = max(c.winfo_width(), 100)
        height = FX_HEIGHT
        self._fx_keys = {k.note: k for k in piano_layout.layout(width, PIANO_HEIGHT)}
        c.configure(bg=p["piano_bg"])
        c.delete("floor")
        line = theme.mix(p["piano_bg"], p["grid"], 0.28 if self.scheme == theme.DARK else 0.18)
        for k in range(1, 6):
            y = height * (k / 6) ** 1.6
            c.create_line(0, y, width, y, fill=line, tags=("floor",))
        vx = width / 2
        for i in range(-16, 17):
            c.create_line(vx + i * width / 50, 0, vx + i * width / 14, height, fill=line, tags=("floor",))
        c.tag_lower("floor")


    def _on_note_event(self, event):
        """NoteBus feliratkozó: a hangok az effekt modellbe kerülnek."""
        if not self.fx_enabled_var.get() or not piano_layout.FIRST_NOTE <= event.note <= piano_layout.LAST_NOTE:
            return
        if event.on:
            self.visualizer.note_on(event.note, event.velocity)
        else:
            self.visualizer.note_off(event.note)
        self._start_fx()

    def _start_fx(self):
        if self.fx_job is None and self.visualizer.active:
            self.fx_job = self.root.after(FX_FRAME_MS, self._fx_tick)


    def _fx_tick(self):
        """Egy képkocka; csak addig fut, amíg van mit rajzolni."""
        self.fx_job = None
        started = time.monotonic()
        if not self.fx_enabled_var.get():
            self._fx_hide_from({"rect": 0, "oval": 0})
            return
        c, p = self.fx_canvas, self.palette
        bg = p["piano_bg"]
        colors = {False: p["key_white_active"], True: p["key_black_active"]}
        width = max(c.winfo_width(), 100)
        # a vászon elemeit újrahasznosítjuk (mozgatás + átszínezés), nem töröljük / hozzuk létre minden képkockán
        used = {"rect": 0, "oval": 0}
        for s in self.visualizer.frame(time.monotonic(), width, FX_HEIGHT, self._fx_key_span):
            kind = "oval" if s.kind == "spark" else "rect"
            pool = self._fx_pool[kind]
            if used[kind] == len(pool):
                create = c.create_oval if kind == "oval" else c.create_rectangle
                pool.append(create(0, 0, 0, 0, outline="", tags=("fx",)))
            item = pool[used[kind]]
            used[kind] += 1
            c.coords(item, s.x0, s.y0, s.x1, s.y1)
            c.itemconfigure(item, fill=theme.mix(bg, colors[s.black], min(max(s.intensity, 0.0), 1.0)), state="normal")
        self._fx_hide_from(used)
        if self.visualizer.active:
            # ha egy képkocka mégis sokáig tart, ritkábban rajzolunk — a hangok időzítése az első
            elapsed_ms = (time.monotonic() - started) * 1000
            self.fx_job = self.root.after(max(FX_FRAME_MS, int(2 * elapsed_ms)), self._fx_tick)


    def _fx_hide_from(self, used):
        """A most nem használt (de előző képkockán látható) elemek elrejtése."""
        for kind, pool in self._fx_pool.items():
            for item in pool[used[kind]:self._fx_shown[kind]]:
                self.fx_canvas.itemconfigure(item, state="hidden")
            self._fx_shown[kind] = used[kind]


    def on_fx_toggle(self):
        enabled = self.fx_enabled_var.get()
        theme.save_setting("visual_fx", enabled)
        if enabled:
            self.fx_canvas.pack(fill="x", padx=8, pady=(6, 0), before=self.canvas)
            for note in self.active_notes:  # a már szóló hangok is kapjanak oszlopot
                self.visualizer.note_on(note, 100)
            self._start_fx()
        else:
            self.visualizer.clear()
            self._fx_hide_from({"rect": 0, "oval": 0})
            self.fx_canvas.pack_forget()
