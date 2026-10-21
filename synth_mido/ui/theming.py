"""Megjelenés: a választott skin alkalmazása minden widgetre, fejléc, skin / változat váltás,
rendszer téma figyelése."""

import tkinter as tk
from tkinter import font as tkfont

from synth_mido.skins import registry, theme
from synth_mido.skins.palette import mix
from synth_mido.ui.common import THEME_POLL_MS


class ThemingMixin:
    # --- állapot ------------------------------------------------------------------

    def _init_skin(self):
        self.skin_id, self.variant = theme.load_skin()
        self.skin = registry.get(self.skin_id)
        self.scheme = theme.resolve_scheme(self.variant)
        self.palette = self.skin.palette(self.scheme)
        self.font_family = theme.FONT_FAMILY
        self.skin_listeners = []  # további ablakok (pl. hangszínszabályzó), amelyek skin váltáskor újrastílusoznak

    def set_skin(self, skin_id: str, variant: str, save: bool = True):
        self.skin = registry.get(skin_id)
        self.skin_id, self.variant = self.skin.id, variant
        self.skin_var.set(self.skin.name)
        self.variant_var.set(registry.VARIANT_LABELS[variant])
        self.scheme = theme.resolve_scheme(variant)
        self.palette = self.skin.palette(self.scheme)
        if save:
            theme.save_skin(self.skin_id, self.variant)
        self.apply_theme()
        self._schedule_theme_poll()

    def on_skin_change(self, _event=None):
        skin = registry.by_name(self.skin_var.get()) or registry.get(registry.DEFAULT_SKIN)
        self.set_skin(skin.id, self.variant)

    def on_variant_change(self, _event=None):
        label = self.variant_var.get()
        variant = next((v for v, text in registry.VARIANT_LABELS.items() if text == label), registry.DEFAULT_VARIANT)
        self.set_skin(self.skin_id, variant)

    # --- alkalmazás ------------------------------------------------------------------

    def apply_theme(self):
        """Az aktív skin (paletta + widget stílus tokenek) alkalmazása minden widgetre."""
        p, st = self.palette, self.skin.style
        self.font_family = registry.choose_font(self.skin.fonts, tkfont.families(self.root))
        font = (self.font_family, theme.FONT_SIZE)
        bold = (self.font_family, theme.FONT_SIZE, "bold")
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            try:
                tkfont.nametofont(name).configure(family=self.font_family, size=theme.FONT_SIZE)
            except tk.TclError:
                pass
        for frame, title in self.sections:
            frame.configure(text=f" {title.upper()} " if st.title_upper else title)
        edge = p[st.button_edge]
        # a clam téma "flat" reliefnél semmilyen keretet nem rajzol: a lapos skinek "raised" reliefet kapnak
        # egyszínű (felülettel azonos) fénnyel / árnyékkal — így lapos marad, de a keret látszik
        button_relief = "raised" if st.relief == "flat" else st.relief

        style = self.style
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        self.root.configure(bg=p["bg"])

        style.configure(
            ".", background=p["bg"], foreground=p["fg"], fieldbackground=p["surface"], bordercolor=p["border"],
            lightcolor=p["border"], darkcolor=p["border"], troughcolor=p["surface"], focuscolor=p["accent"],
            selectbackground=p["select_bg"], selectforeground=p["fg"], insertcolor=p["fg"], font=font,
        )
        style.configure("TFrame", background=p["bg"])
        style.configure("TLabel", background=p["bg"], foreground=p["fg"])
        style.configure("Status.TLabel", background=p["bg"], foreground=p["muted"])
        style.configure("TLabelframe", background=p["bg"], bordercolor=p["border"], relief=st.frame_relief,
                        borderwidth=st.border_width)
        style.configure("TLabelframe.Label", background=p["bg"], foreground=p["section_fg"], font=bold)

        # gombok: alak (padding, keret, dombormű) és minden állapot színe a skinből
        style.configure("TButton", background=p["surface"], foreground=p["fg"], bordercolor=edge,
                        lightcolor=mix(p["surface"], "#ffffff", 0.12) if st.relief != "flat" else p["surface"],
                        darkcolor=mix(p["surface"], "#000000", 0.25) if st.relief != "flat" else p["surface"],
                        relief=button_relief, borderwidth=st.border_width, padding=st.button_padding,
                        font=bold if st.bold_buttons else font)
        style.map(
            "TButton",
            background=[("pressed", mix(p["select_bg"], p["accent"], 0.2)), ("active", p["select_bg"]), ("disabled", p["bg"])],
            foreground=[("disabled", p["muted"])],
            bordercolor=[("active", p["accent"]), ("disabled", p["border"])],
            lightcolor=[("active", p["select_bg"])],
            darkcolor=[("active", p["select_bg"])],
            relief=[("pressed", "sunken" if st.relief != "flat" else "flat")],
        )
        # tömör gomb a zsúfolt sorokhoz: minden színt / állapotot a TButton-tól örököl
        style.configure("Small.TButton", padding=(max(6, st.button_padding[0] - 5), st.button_padding[1]))
        style.configure("Accent.TButton", background=p["accent"], foreground=p["accent_fg"], bordercolor=p["accent"],
                        lightcolor=p["accent"], darkcolor=p["accent"], relief=button_relief, borderwidth=st.border_width,
                        padding=st.button_padding, font=bold)
        style.map(
            "Accent.TButton",
            background=[("pressed", mix(p["accent"], "#000000", 0.15)), ("active", mix(p["accent"], "#ffffff", 0.12)),
                        ("disabled", p["bg"])],
            foreground=[("disabled", p["muted"])],
            bordercolor=[("active", p["accent2"])],
        )

        style.configure("TCheckbutton", background=p["bg"], foreground=p["fg"], indicatorbackground=p["surface"],
                        indicatorforeground=p["accent"], indicatormargin=(0, 0, 6, 0))
        style.map("TCheckbutton", background=[("active", p["bg"])], foreground=[("disabled", p["muted"])],
                  indicatorbackground=[("pressed", p["select_bg"]), ("selected", p["surface"])])
        style.map("Pedal.TCheckbutton", foreground=[("selected", p["accent"])], background=[("active", p["bg"])],
                  indicatorbackground=[("selected", p["accent"])])

        style.configure("TCombobox", background=p["surface"], foreground=p["fg"], fieldbackground=p["surface"],
                        arrowcolor=p["accent2"] if st.button_edge == "accent2" else p["fg"], bordercolor=p["border"],
                        padding=4)
        style.map("TCombobox", fieldbackground=[("readonly", p["surface"])], foreground=[("readonly", p["fg"])],
                  selectbackground=[("readonly", p["surface"])], selectforeground=[("readonly", p["fg"])],
                  background=[("active", p["select_bg"])], bordercolor=[("focus", p["accent"]), ("active", p["accent2"])])
        style.configure("Horizontal.TScale", background=p["accent2"], troughcolor=mix(p["bg"], p["border"], 0.7),
                        bordercolor=p["border"], lightcolor=p["accent2"], darkcolor=p["accent2"])
        style.map("Horizontal.TScale", background=[("disabled", p["border"]), ("active", p["accent"])])
        style.configure("TEntry", fieldbackground=p["surface"], foreground=p["fg"], insertcolor=p["fg"], padding=4,
                        bordercolor=p["border"])
        style.map("TEntry", bordercolor=[("focus", p["accent"])])
        style.configure("Treeview", background=p["surface"], fieldbackground=p["surface"], foreground=p["fg"],
                        bordercolor=p["border"], rowheight=24)
        style.map("Treeview", background=[("selected", p["select_bg"])], foreground=[("selected", p["fg"])])
        style.configure("Treeview.Heading", background=p["bg"], foreground=p["section_fg"], bordercolor=p["border"],
                        relief="flat", font=bold)
        style.map("Treeview.Heading", background=[("active", p["select_bg"])])
        style.configure("TScrollbar", background=p["surface"], troughcolor=p["bg"], bordercolor=p["border"],
                        arrowcolor=p["accent2"])
        style.map("TScrollbar", background=[("active", p["select_bg"]), ("pressed", p["accent2"])])

        self.root.option_add("*TCombobox*Listbox.background", p["surface"])
        self.root.option_add("*TCombobox*Listbox.foreground", p["fg"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", p["select_bg"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", p["fg"])
        self._restyle_combobox_popdowns()

        self.canvas.configure(bg=p["piano_bg"])
        self.log.configure(
            bg=p["log_bg"], fg=p["log_fg"], insertbackground=p["log_fg"], selectbackground=p["select_bg"],
            selectforeground=p["fg"], relief="flat", highlightthickness=1, highlightbackground=p["border"],
            highlightcolor=p["accent"], padx=6, pady=4, font=font,
        )
        for win in (self.save_dialog, self.records_win):
            if win is not None and win.winfo_exists():
                win.configure(bg=p["bg"])
        if self.records_tree is not None:
            self.records_tree.tag_configure("error", foreground=p["muted"])
        self.draw_header()
        self.draw_fx_floor()
        self.draw_piano()
        for listener in list(self.skin_listeners):
            listener()

    def draw_header(self):
        """A skin fejléc jelenete (Strategy: a skin saját rajzolója)."""
        c, skin = self.header, self.skin
        width = max(c.winfo_width(), 200)
        height = skin.header_height
        c.configure(height=height, bg=self.palette["header_bg"])
        c.delete("all")
        if skin.painter:
            skin.painter(c, width, height, self.palette, self.font_family, self.scheme == theme.DARK)

    def _restyle_combobox_popdowns(self):
        """A már létrehozott legördülő listák színezése (az option_add csak az újakra hat)."""
        p = self.palette
        for combo in self.comboboxes():
            try:
                popdown = self.root.tk.call("ttk::combobox::PopdownWindow", str(combo))
                listbox = self.root.nametowidget(f"{popdown}.f.l")
                listbox.configure(background=p["surface"], foreground=p["fg"], selectbackground=p["select_bg"],
                                  selectforeground=p["fg"])
            except (tk.TclError, KeyError):
                pass

    def comboboxes(self):
        return [getattr(self, n) for n in ("input_combo", "output_combo", "skin_combo", "variant_combo",
                                           "instrument_combo", "speed_combo", "doubling_combo") if hasattr(self, n)]

    # --- rendszer téma figyelése ------------------------------------------------------

    def _schedule_theme_poll(self):
        """A "Rendszer" változatnál az OS séma figyelése; Sötét / Világos választásnál nincs figyelés."""
        if self.theme_job:
            self.root.after_cancel(self.theme_job)
            self.theme_job = None
        if self.variant == theme.SYSTEM:
            self.theme_job = self.root.after(THEME_POLL_MS, self._poll_system_theme)

    def _poll_system_theme(self):
        self.theme_job = None
        if self.variant != theme.SYSTEM:
            return
        scheme = theme.detect_system_theme()
        if scheme != self.scheme:
            self.scheme = scheme
            self.palette = self.skin.palette(scheme)
            self.apply_theme()
        self.theme_job = self.root.after(THEME_POLL_MS, self._poll_system_theme)
