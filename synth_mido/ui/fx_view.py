"""Hangeffekt sáv a zongora fölött: a választott effekt (Strategy) általános, készletező rajzolója.

A rajzoló nem ismeri az egyes effekteket: az effekt szerepeket ad (`LAYERS`), szerepenként
vászon elem fajtát (`KINDS`) és színt (`colors`); a vászon elemeit szerepenként
újrahasznosítjuk (mozgatás + átszínezés), nem töröljük és hozzuk létre minden képkockán.
"""

import time

from synth_mido.core import piano_layout
from synth_mido.fx import effects
from synth_mido.skins import theme
from synth_mido.ui.common import (
    FX_FRAME_MS,
    FX_HEIGHT,
    PIANO_HEIGHT,
)
from synth_mido.ui.equalizer_window import EqualizerWindow

SETTING_KEY = "fx_effect"


class FxMixin:

    def _init_effect(self):
        """Indításkor: a mentett effekt, különben a skinhez illő."""
        self.effect_id = theme.load_setting(SETTING_KEY, self.skin.effect)
        if self.effect_id not in effects.EFFECTS:
            self.effect_id = self.skin.effect
        self.visualizer = effects.create(self.effect_id)
        self._fx_pool, self._fx_shown, self._fx_fonts = {}, {}, {}


    def set_effect(self, effect_id: str, save: bool = True):
        """Effekt váltása: az eddigi elemek törlődnek, a már szóló hangok az új effekttel folytatódnak."""
        if effect_id not in effects.EFFECTS:
            effect_id = effects.DEFAULT
        self.effect_id = effect_id
        self.visualizer = effects.create(effect_id)
        self.fx_canvas.delete("fx")
        self._fx_pool, self._fx_shown, self._fx_fonts = {}, {}, {}
        self._fx_warm_fonts()
        self.effect_var.set(effects.label(effect_id))
        if save:
            theme.save_setting(SETTING_KEY, effect_id)
        if self.fx_enabled_var.get():
            for note in sorted(self.active_notes):
                self.visualizer.note_on(note, 100)
            self._start_fx()


    def _fx_warm_fonts(self):
        """A jeles effektek (hópehely, ♪, π …) jeleinek betűtípusát előre betöltjük a látható területen kívül:
        az első megjelenítés (tartalék betűtípus keresése) különben egy képkockát akár 100 ms-ig is megakaszt."""
        fx, c = self.visualizer, self.fx_canvas
        for size in fx.TEXT_SIZES:
            c.create_text(-1000, -1000, text=fx.TEXT_SAMPLE, font=(self.font_family, size), tags=("fx-warm",))
        if fx.TEXT_SIZES:
            c.bbox("fx-warm")   # a mérés kényszeríti a betöltést
            c.delete("fx-warm")


    def on_effect_change(self, _event=None):
        index = self.effect_combo.current()  # index szerint: a név nyelvfüggő
        ids = effects.ids()
        self.set_effect(ids[index] if 0 <= index < len(ids) else effects.DEFAULT)


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
        self._fx_warm_fonts()  # skinváltáskor a betűtípus is változhat


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


    def _fx_new_item(self, role: str, size: float):
        c, fx = self.fx_canvas, self.visualizer
        kind, tags = fx.KINDS[role], ("fx", "fx-" + role)
        if kind == "poly":
            return c.create_polygon(0, 0, 0, 0, 0, 0, outline="", smooth=role in fx.SMOOTH, tags=tags)
        if kind == "rect":
            return c.create_rectangle(0, 0, 0, 0, outline="", tags=tags)
        if kind == "ring":
            return c.create_oval(0, 0, 0, 0, fill="", width=1.5, tags=tags)
        if kind == "text":
            return c.create_text(0, 0, text="", tags=tags)
        return c.create_oval(0, 0, 0, 0, outline="", tags=tags)


    def _fx_tick(self):
        """Egy képkocka; csak addig fut, amíg van mit rajzolni."""
        self.fx_job = None
        started = time.monotonic()
        if not self.fx_enabled_var.get():
            self._fx_hide_from({})
            return
        c, p, fx = self.fx_canvas, self.palette, self.visualizer
        bg = p["piano_bg"]
        colors = fx.colors(p, self.scheme == theme.DARK)
        width = max(c.winfo_width(), 100)
        used = {}
        created = False
        for s in fx.frame(time.monotonic(), width, FX_HEIGHT, self._fx_key_span):
            pool = self._fx_pool.setdefault(s.role, [])
            n = used.get(s.role, 0)
            if n == len(pool):
                pool.append(self._fx_new_item(s.role, s.size))
                created = True
            item = pool[n]
            used[s.role] = n + 1
            c.coords(item, *s.points)
            color = theme.mix(bg, colors[s.role][s.black], min(max(s.intensity, 0.0), 1.0))
            kind = fx.KINDS[s.role]
            if kind == "ring":
                c.itemconfigure(item, outline=color, state="normal")
            elif kind == "text":
                font = (self.font_family, int(s.size))
                if self._fx_fonts.get(item) != (font, s.text):  # betűtípus / jel csak ha változik (drága)
                    self._fx_fonts[item] = (font, s.text)
                    c.itemconfigure(item, font=font, text=s.text)
                c.itemconfigure(item, fill=color, state="normal")
            else:
                c.itemconfigure(item, fill=color, state="normal")
        if created:  # új elem a tetejére kerül — a rétegek sorrendjét helyreállítjuk
            for role in fx.LAYERS[1:]:
                c.tag_raise("fx-" + role)
        self._fx_hide_from(used)
        if fx.active:
            # ha egy képkocka mégis sokáig tart, ritkábban rajzolunk — a hangok időzítése az első
            elapsed_ms = (time.monotonic() - started) * 1000
            self.fx_job = self.root.after(max(FX_FRAME_MS, int(2 * elapsed_ms)), self._fx_tick)


    def _fx_hide_from(self, used):
        """A most nem használt (de előző képkockán látható) elemek elrejtése."""
        for role, pool in self._fx_pool.items():
            n = used.get(role, 0)
            for item in pool[n:self._fx_shown.get(role, 0)]:
                self.fx_canvas.itemconfigure(item, state="hidden")
            self._fx_shown[role] = n


    def open_equalizer(self):
        """A Winamp-szerű hangszínszabályzó ablak megnyitása (ha már nyitva van, előtérbe hozza)."""
        if self.eq_window is not None and self.eq_window.exists():
            self.eq_window.focus()
            return
        self.eq_window = EqualizerWindow(self)

    def on_fx_toggle(self):
        enabled = self.fx_enabled_var.get()
        theme.save_setting("visual_fx", enabled)
        if enabled:
            self.fx_canvas.pack(fill="x", padx=8, pady=(6, 0), before=self.canvas)
            for note in self.active_notes:  # a már szóló hangok is kapjanak effektet
                self.visualizer.note_on(note, 100)
            self._start_fx()
        else:
            self.visualizer.clear()
            self._fx_hide_from({})
            self.fx_canvas.pack_forget()
