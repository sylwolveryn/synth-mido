"""Téma: stílusok, fejléc, téma váltás és rendszer téma figyelése."""

import tkinter as tk
from tkinter import font as tkfont

from synth_mido.skins import theme
from synth_mido.ui.common import (
    HEADER_HEIGHT,
    HEADER_HEIGHT_PLAIN,
    THEME_LABELS,
    THEME_POLL_MS,
)


class ThemingMixin:

    def apply_theme(self):
        """Az aktív paletta alkalmazása az összes (már létező) widgetre."""
        p = self.palette
        synth = self.scheme == theme.SYNTHWAVE_MODE
        self.font_family = theme.display_font(tkfont.families(self.root)) if synth else theme.FONT_FAMILY
        font = (self.font_family, theme.FONT_SIZE)
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                tkfont.nametofont(name).configure(family=self.font_family, size=theme.FONT_SIZE)
            except tk.TclError:
                pass
        for frame, title in self.sections:
            frame.configure(text=f" {title.upper()} " if synth else title)
        # Synthwave: lapos neon keret a gombokon; a többi témában a megszokott szürke keret
        edge = p["accent2"] if synth else p["border"]

        style = self.style
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.root.configure(bg=p["bg"])

        style.configure(
            ".",
            background=p["bg"],
            foreground=p["fg"],
            fieldbackground=p["surface"],
            bordercolor=p["border"],
            lightcolor=p["border"],
            darkcolor=p["border"],
            troughcolor=p["surface"],
            focuscolor=p["accent"],
            selectbackground=p["select_bg"],
            selectforeground=p["fg"],
            insertcolor=p["fg"],
            font=font,
        )
        style.configure("TFrame", background=p["bg"])
        style.configure("TLabel", background=p["bg"], foreground=p["fg"])
        style.configure("TCheckbutton", background=p["bg"], foreground=p["fg"], indicatorbackground=p["surface"],
                        indicatorforeground=p["accent"])
        style.map("TCheckbutton", background=[("active", p["bg"])], indicatorbackground=[("selected", p["surface"])])
        style.map("Pedal.TCheckbutton", foreground=[("selected", p["accent"])], background=[("active", p["bg"])],
                  indicatorbackground=[("selected", p["accent"])])
        style.configure("Status.TLabel", background=p["bg"], foreground=p["muted"])
        style.configure("TLabelframe", background=p["bg"], bordercolor=p["border"], relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=p["bg"], foreground=p["section_fg"],
                        font=(self.font_family, theme.FONT_SIZE, "bold"))

        style.configure("TButton", background=p["surface"], foreground=p["fg"], bordercolor=edge,
                        lightcolor=p["surface"], darkcolor=p["surface"], padding=(12, 5))
        style.map(
            "TButton",
            background=[("pressed", p["select_bg"]), ("active", p["select_bg"]), ("disabled", p["bg"])],
            foreground=[("disabled", p["muted"])],
            bordercolor=[("active", p["accent"]), ("disabled", p["border"])],
            lightcolor=[("active", p["select_bg"])],
            darkcolor=[("active", p["select_bg"])],
        )
        style.configure("Accent.TButton", background=p["accent"], foreground=p["accent_fg"], bordercolor=p["accent"],
                        lightcolor=p["accent"], darkcolor=p["accent"], padding=(12, 5),
                        font=(self.font_family, theme.FONT_SIZE, "bold"))
        style.map(
            "Accent.TButton",
            background=[("pressed", p["accent"]), ("active", p["accent"]), ("disabled", p["bg"])],
            foreground=[("disabled", p["muted"])],
            bordercolor=[("active", p["accent2"])],
        )

        style.configure(
            "TCombobox",
            background=p["surface"],
            foreground=p["fg"],
            fieldbackground=p["surface"],
            arrowcolor=p["fg"],
            bordercolor=p["border"],
            padding=4,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", p["surface"])],
            foreground=[("readonly", p["fg"])],
            selectbackground=[("readonly", p["surface"])],
            selectforeground=[("readonly", p["fg"])],
            background=[("active", p["select_bg"])],
        )
        style.configure("Horizontal.TScale", background=p["accent2"], troughcolor=p["border"], bordercolor=p["border"],
                        lightcolor=p["accent2"], darkcolor=p["accent2"])
        style.map("Horizontal.TScale", background=[("disabled", p["border"])])
        style.configure("TEntry", fieldbackground=p["surface"], foreground=p["fg"], insertcolor=p["fg"], padding=4)
        style.configure(
            "Treeview",
            background=p["surface"],
            fieldbackground=p["surface"],
            foreground=p["fg"],
            bordercolor=p["border"],
            rowheight=24,
        )
        style.map("Treeview", background=[("selected", p["select_bg"])], foreground=[("selected", p["fg"])])
        style.configure("Treeview.Heading", background=p["bg"], foreground=p["muted"], bordercolor=p["border"], relief="flat")
        style.map("Treeview.Heading", background=[("active", p["select_bg"])])
        style.configure(
            "TScrollbar",
            background=p["surface"],
            troughcolor=p["bg"],
            bordercolor=p["border"],
            arrowcolor=p["fg"],
        )
        style.map("TScrollbar", background=[("active", p["select_bg"])])

        self.root.option_add("*TCombobox*Listbox.background", p["surface"])
        self.root.option_add("*TCombobox*Listbox.foreground", p["fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", p["select_bg"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", p["fg"])
        self._restyle_combobox_popdowns()

        self.canvas.configure(bg=p["piano_bg"])
        self.log.configure(
            bg=p["log_bg"],
            fg=p["log_fg"],
            insertbackground=p["log_fg"],
            selectbackground=p["select_bg"],
            selectforeground=p["fg"],
            relief="flat",
            highlightthickness=1,
            highlightbackground=p["border"],
            highlightcolor=p["accent"],
            padx=6,
            pady=4,
            font=font,
        )
        for win in (self.save_dialog, self.records_win):
            if win is not None and win.winfo_exists():
                win.configure(bg=p["bg"])
        if self.records_tree is not None:
            self.records_tree.tag_configure("error", foreground=p["muted"])
        self.draw_header()
        self.draw_fx_floor()
        self.draw_piano()


    def draw_header(self):
        """Fejléc: Synthwave-ben naplemente nap + perspektivikus neon rács, máshol egyszerű címsor."""
        c, p = self.header, self.palette
        width = max(c.winfo_width(), 200)
        synth = self.scheme == theme.SYNTHWAVE_MODE
        height = HEADER_HEIGHT if synth else HEADER_HEIGHT_PLAIN
        c.configure(height=height, bg=p["header_bg"])
        c.delete("all")
        ff = self.font_family
        if not synth:
            c.create_text(12, height / 2, anchor="w", text="SYNTH-MIDO", fill=p["title_fg"], font=(ff, 13, "bold"))
            c.create_text(140, height / 2, anchor="w", text="VEVOR MIDI vezérlő", fill=p["muted"], font=(ff, 9))
            c.create_line(0, height - 1, width, height - 1, fill=p["border"])
            return

        horizon = int(height * 0.64)
        # égbolt: éjszakai lilából a horizont felé izzó bíborba
        bands = 14
        for i in range(bands):
            y0, y1 = horizon * i / bands, horizon * (i + 1) / bands + 1
            c.create_rectangle(0, y0, width, y1, outline="", fill=theme.mix(p["header_bg"], "#4a1260", i / (bands - 1)))
        # nap: függőleges színátmenet, alul egyre vastagabb csíkokkal
        r = height * 0.52
        cx, cy = width - 150, horizon - r * 0.15
        top = int(cy - r)
        for y in range(max(top, 0), horizon):
            dy = y - cy
            if abs(dy) >= r:
                continue
            t = (y - top) / max(horizon - top, 1)
            if t > 0.45 and (y - top) % 7 < 1 + int((t - 0.45) * 8):
                continue  # csík
            half = (r * r - dy * dy) ** 0.5
            color = theme.mix(p["sun_top"], p["sun_mid"], t / 0.5) if t < 0.5 else theme.mix(p["sun_mid"], p["sun_bottom"], (t - 0.5) / 0.5)
            c.create_line(cx - half, y, cx + half, y, fill=color)
        # talaj és perspektivikus rács
        c.create_rectangle(0, horizon, width, height, outline="", fill=theme.mix(p["header_bg"], "#12032b", 0.5))
        vx = width / 2
        for i in range(-14, 15):
            c.create_line(vx + i * width / 70, horizon, vx + i * width / 6, height, fill=theme.mix(p["header_bg"], p["grid"], 0.55))
        rows = 6
        for k in range(1, rows + 1):
            y = horizon + (height - horizon) * (k / rows) ** 2
            c.create_line(0, y, width, y, fill=theme.mix(p["header_bg"], p["grid"], 0.25 + 0.6 * k / rows))
        c.create_line(0, horizon, width, horizon, fill=p["accent"], width=2)
        # cím: cián betűk magenta "árnyékkal", ritkított betűközzel
        title = " ".join("SYNTH-MIDO")
        c.create_text(26, horizon * 0.42 + 2, anchor="w", text=title, fill=p["accent"], font=(ff, 24, "bold"))
        c.create_text(24, horizon * 0.42, anchor="w", text=title, fill=p["accent2"], font=(ff, 24, "bold"))
        c.create_text(26, horizon * 0.42 + 24, anchor="w", text="VEVOR MIDI VEZÉRLŐ  ·  88 BILLENTYŰ",
                      fill=p["sun_top"], font=(ff, 9, "bold"))


    def _restyle_combobox_popdowns(self):
        """A már létrehozott legördülő listák színezése (az option_add csak az újakra hat)."""
        p = self.palette
        for combo in (self.input_combo, self.output_combo, self.instrument_combo, self.theme_combo, self.speed_combo,
                      self.doubling_combo):
            try:
                popdown = self.root.tk.call("ttk::combobox::PopdownWindow", str(combo))
                listbox = self.root.nametowidget(f"{popdown}.f.l")
                listbox.configure(
                    background=p["surface"],
                    foreground=p["fg"],
                    selectbackground=p["select_bg"],
                    selectforeground=p["fg"],
                )
            except (tk.TclError, KeyError):
                pass


    def on_theme_change(self, _event=None):
        label = self.theme_var.get()
        mode = next((m for m, text in THEME_LABELS.items() if text == label), theme.DEFAULT_MODE)
        self.set_theme_mode(mode)
        theme.save_mode(mode)


    def set_theme_mode(self, mode: str):
        self.theme_mode = mode
        self.theme_var.set(THEME_LABELS[mode])
        self.scheme = theme.resolve_scheme(mode)
        self.palette = theme.palette_for(self.scheme)
        self.apply_theme()
        self._schedule_theme_poll()


    def _schedule_theme_poll(self):
        """Rendszer módban az OS séma figyelése; Világos/Sötét módban nincs figyelés."""
        if self.theme_job:
            self.root.after_cancel(self.theme_job)
            self.theme_job = None
        if self.theme_mode == theme.SYSTEM_MODE:
            self.theme_job = self.root.after(THEME_POLL_MS, self._poll_system_theme)


    def _poll_system_theme(self):
        self.theme_job = None
        if self.theme_mode != theme.SYSTEM_MODE:
            return
        scheme = theme.detect_system_theme()
        if scheme != self.scheme:
            self.scheme = scheme
            self.palette = theme.palette_for(scheme)
            self.apply_theme()
        self.theme_job = self.root.after(THEME_POLL_MS, self._poll_system_theme)
