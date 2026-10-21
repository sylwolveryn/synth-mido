"""Winamp-szerű hangszínszabályzó ablak: spektrum analizátor választható animációkkal.

A NoteBus-ra iratkozik fel (Observer), így minden hangforrásra reagál; a színeket
az aktuális skinből veszi, és skin váltáskor újrastílusoz. Az animáció csak akkor
fut, ha az ablak nyitva van és van mozgás; a vászon elemeit újrahasznosítja.
"""

import time
import tkinter as tk
from tkinter import ttk

from synth_mido.core.i18n import t
from synth_mido.fx import animations
from synth_mido.fx.spectrum import Spectrum
from synth_mido.skins import theme
from synth_mido.skins.palette import mix

FRAME_MS = 33          # ~30 képkocka / mp
ROLE_TOKENS = {"low": "accent2", "mid": "sun_mid", "high": "accent", "peak": "title_fg", "line": "accent2",
               "grid": "border"}
SETTING_KEY = "eq_animation"


class EqualizerWindow:
    def __init__(self, app):
        self.app = app
        self.win = tk.Toplevel(app.root)
        app.bind_text(self.win, lambda: t("eq.title"), option="title")
        self.win.geometry("680x340")
        self.win.minsize(360, 200)
        self.spectrum = Spectrum()
        saved = theme.load_setting(SETTING_KEY, animations.DEFAULT)
        self.animation = animations.create(saved)
        self.job = None
        self._pool = {"rect": [], "line": [], "oval": [], "poly": []}
        self._shown = {k: 0 for k in self._pool}

        bar = ttk.Frame(self.win, padding=(10, 8))
        bar.pack(fill="x")
        app.tr(ttk.Label(bar), "eq.animation").pack(side="left")
        self.anim_var = tk.StringVar()
        self.anim_combo = ttk.Combobox(bar, textvariable=self.anim_var, state="readonly", width=20)
        app.bind_text(self.anim_combo, self._relabel_animations, option=None)
        self.anim_combo.pack(side="left", padx=8)
        self.anim_combo.bind("<<ComboboxSelected>>", self.on_animation_change)
        self.info_var = tk.StringVar()
        ttk.Label(bar, textvariable=self.info_var, style="Status.TLabel").pack(side="right")

        self.canvas = tk.Canvas(self.win, highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.canvas.bind("<Configure>", lambda _e: self._redraw_static())

        self._unsubscribe = app.notes.subscribe(self._on_note)
        app.skin_listeners.append(self.restyle)
        self.win.protocol("WM_DELETE_WINDOW", self.close)
        self.win.bind("<Escape>", lambda _e: self.close())
        for note in sorted(app.active_notes):  # ami már szól, az is megjelenik
            self.spectrum.note_on(note, 100)
        self.restyle()
        self._start()

    # --- életciklus -----------------------------------------------------------------

    def exists(self) -> bool:
        try:
            return bool(self.win.winfo_exists())
        except tk.TclError:
            return False

    def focus(self):
        self.win.deiconify()
        self.win.lift()
        self.win.focus_force()

    def close(self):
        if self.job is not None:
            self.win.after_cancel(self.job)
            self.job = None
        self._unsubscribe()
        if self.restyle in self.app.skin_listeners:
            self.app.skin_listeners.remove(self.restyle)
        if self.exists():
            self.win.destroy()
        if getattr(self.app, "eq_window", None) is self:
            self.app.eq_window = None

    # --- események -------------------------------------------------------------------

    def _on_note(self, event):
        if event.on:
            self.spectrum.note_on(event.note, event.velocity)
        else:
            self.spectrum.note_off(event.note)
        self._start()

    def on_animation_change(self, _event=None):
        ids = list(animations.ANIMATIONS)
        index = self.anim_combo.current()  # index szerint: a név nyelvfüggő
        anim_id = ids[index] if 0 <= index < len(ids) else animations.DEFAULT
        self.animation = animations.create(anim_id)
        theme.save_setting(SETTING_KEY, anim_id)
        self.win.focus_set()
        self._hide_from({k: 0 for k in self._pool})
        self._redraw_static()

    def _relabel_animations(self):
        self.anim_combo.configure(values=[animations.label(k) for k in animations.ANIMATIONS])
        self.anim_var.set(animations.label(self.animation.id))

    def restyle(self):
        """Skin váltás: háttér, LED rács és a következő képkocka színei."""
        p = self.app.palette
        self.bg = mix(p["piano_bg"], "#000000", 0.35) if self.app.scheme == theme.DARK else p["piano_bg"]
        self.win.configure(bg=p["bg"])
        self.canvas.configure(bg=self.bg)
        self.colors = {role: p[token] for role, token in ROLE_TOKENS.items()}
        self._redraw_static()

    # --- rajzolás --------------------------------------------------------------------

    def _start(self):
        if self.job is None and self.exists():
            self.job = self.win.after(FRAME_MS, self._tick)

    def _redraw_static(self):
        """LED rács (csak a klasszikus oszlopoknál) + egy képkocka, akkor is, ha épp csend van."""
        c = self.canvas
        c.delete("grille")
        w, h = max(c.winfo_width(), 50), max(c.winfo_height(), 50)
        rows = self.animation.led_rows
        if rows:
            for k in range(1, rows):
                y = h * k / rows
                c.create_line(0, y, w, y, fill=self.bg, width=2, tags=("grille",))
        self._render()

    def _tick(self):
        self.job = None
        if not self.exists():
            return
        started = time.monotonic()
        self.spectrum.step()
        self._render()
        if self.spectrum.active or self.animation.id == "scope":
            # ha egy képkocka lassú, ritkábban rajzolunk — a hangok időzítése az első
            delay = max(FRAME_MS, int(2000 * (time.monotonic() - started)))
            self.job = self.win.after(delay, self._tick)

    def _render(self):
        c = self.canvas
        w, h = max(c.winfo_width(), 50), max(c.winfo_height(), 50)
        used = {k: 0 for k in self._pool}
        for shape in self.animation.render(self.spectrum, w, h):
            pool = self._pool[shape.kind]
            if used[shape.kind] == len(pool):
                pool.append(self._create(shape.kind))
            item = pool[used[shape.kind]]
            used[shape.kind] += 1
            color = mix(self.bg, self.colors[shape.role], min(max(shape.intensity, 0.0), 1.0))
            c.coords(item, *shape.coords)
            if shape.kind == "line":
                c.itemconfigure(item, fill=color, width=shape.width, state="normal")
            else:
                c.itemconfigure(item, fill=color, state="normal")
        self._hide_from(used)
        c.tag_raise("grille")
        loud = max(self.spectrum.levels) if self.spectrum.levels else 0
        self.info_var.set(f"{animations.label(self.animation.id)} · {round(loud * 100):3d}%")

    def _create(self, kind):
        c = self.canvas
        if kind == "rect":
            return c.create_rectangle(0, 0, 0, 0, outline="", tags=("eq",))
        if kind == "oval":
            return c.create_oval(0, 0, 0, 0, outline="", tags=("eq",))
        if kind == "poly":
            return c.create_polygon(0, 0, 0, 0, 0, 0, outline="", tags=("eq",))
        return c.create_line(0, 0, 0, 0, capstyle="round", joinstyle="round", tags=("eq",))

    def _hide_from(self, used):
        for kind, pool in self._pool.items():
            for item in pool[used[kind]:self._shown[kind]]:
                self.canvas.itemconfigure(item, state="hidden")
            self._shown[kind] = used[kind]
