import os
import subprocess
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont

import config
import doubling
import keyboard_play
import piano_layout
import playback
import recorder
import theme
from midi_controller import VevorMIDIController
from piano_layout import note_label
from sustain import SustainPedal
from visualizer import Visualizer

C_MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71, 72]
C_MAJOR_CHORD = [60, 64, 67]
DEMO_MELODY = [
    76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 68, 71, 72, 64,
    76, 75, 76, 75, 76, 71, 74, 72, 69,
]
PIANO_HEIGHT = 150


def pretty_instrument(name: str) -> str:
    return name.replace("_", " ").title()


def format_seconds(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def speed_label(speed: float) -> str:
    return f"{speed:g}x"


THEME_LABELS = {
    theme.SYNTHWAVE_MODE: "Synthwave",
    theme.SYSTEM_MODE: "Rendszer",
    theme.LIGHT_MODE: "Világos",
    theme.DARK_MODE: "Sötét",
}
THEME_POLL_MS = 2000
HEADER_HEIGHT = 92        # Synthwave fejléc
HEADER_HEIGHT_PLAIN = 34  # egyszerű címsor a többi témában
RECORD_TICK_MS = 250
PLAYER_TICK_MS = 100
FX_HEIGHT = 96      # px — a hangvizualizáció sávja a zongora fölött
FX_FRAME_MS = 33    # ~30 képkocka / mp
SEEK_MARGIN = 8  # px — a csúszka két végén a fogantyú fele


class PianoApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VEVOR MIDI vezérlő")
        self.root.minsize(780, 800)
        self.root.geometry("860x940")

        self.controller = VevorMIDIController()
        self.listening = False
        self.playing = False
        self.play_job = None
        self.listen_job = None
        self.active_notes = set()
        self.held_notes = set()
        self.key_ids = {}

        self.recorder = recorder.Recorder()
        self.record_job = None
        self.save_dialog = None
        self.records_win = None
        self.records_tree = None
        self.fallback_error_logged = False
        self.base_status = ""
        self.player = playback.Player(
            after=self.root.after,
            cancel=self.root.after_cancel,
            on_note=self._on_player_note,
            on_finish=self._on_player_finish,
        )

        self.theme_mode = theme.load_mode()
        self.scheme = theme.resolve_scheme(self.theme_mode)
        self.palette = theme.palette_for(self.scheme)
        self.theme_job = None
        self.style = ttk.Style(self.root)
        self.font_family = theme.FONT_FAMILY

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.instrument_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Nincs csatlakozás")
        self.velocity_var = tk.IntVar(value=100)
        self.theme_var = tk.StringVar(value=THEME_LABELS[self.theme_mode])
        self.record_var = tk.StringVar(value="")
        self.player_name_var = tk.StringVar(value="Nincs betöltött felvétel")
        self.player_time_var = tk.StringVar(value="00:00 / 00:00")
        self.player_pos_var = tk.DoubleVar(value=0.0)
        self.speed_var = tk.StringVar(value=speed_label(1.0))
        self.player_ui_job = None
        self.seeking = False
        self.kb_range_var = tk.StringVar()
        self.show_letters_var = tk.BooleanVar(value=True)
        self.keyboard = keyboard_play.KeyboardPlayer(
            self.root.after, self.root.after_cancel, self._on_keyboard_note, on_range_change=self._on_keyboard_range,
            on_pedal=self.set_pedal,
        )
        self.pedal = SustainPedal(self._stop_note)
        self.pedal_var = tk.BooleanVar(value=False)
        self.visualizer = Visualizer()
        self.fx_enabled_var = tk.BooleanVar(value=bool(theme.load_setting("visual_fx", True)))
        self.fx_job = None
        self._fx_keys = {}
        self._fx_pool = {"rect": [], "oval": []}
        self._fx_shown = {"rect": 0, "oval": 0}
        saved_doubling = theme.load_setting("octave_doubling", doubling.DEFAULT_MODE)
        self.doubler = doubling.OctaveDoubler(saved_doubling)
        self.doubling_var = tk.StringVar(value=doubling.LABELS[self.doubler.mode])

        self._build()
        self.apply_theme()
        self._schedule_theme_poll()
        self.refresh_devices()
        self._activate_output()
        self._refresh_player_ui()
        self._bind_keyboard()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build(self):
        pad = {"padx": 10, "pady": 6}

        self.header = tk.Canvas(self.root, height=HEADER_HEIGHT, highlightthickness=0, bd=0)
        self.header.pack(fill="x")
        self.header.bind("<Configure>", lambda _e: self.draw_header())

        conn = ttk.LabelFrame(self.root, text="Csatlakozás")
        conn.pack(fill="x", **pad)

        ttk.Label(conn, text="Bemenet").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.input_combo = ttk.Combobox(conn, textvariable=self.input_var, state="readonly", width=42)
        self.input_combo.grid(row=0, column=1, sticky="ew", padx=4, pady=6)

        ttk.Label(conn, text="Kimenet").grid(row=1, column=0, sticky="w", padx=8, pady=6)
        self.output_combo = ttk.Combobox(conn, textvariable=self.output_var, state="readonly", width=42)
        self.output_combo.grid(row=1, column=1, sticky="ew", padx=4, pady=6)

        ttk.Label(conn, text="Megjelenés").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.theme_combo = ttk.Combobox(
            conn, textvariable=self.theme_var, values=list(THEME_LABELS.values()), state="readonly", width=16
        )
        self.theme_combo.grid(row=2, column=1, sticky="w", padx=4, pady=6)
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)

        btns = ttk.Frame(conn)
        btns.grid(row=0, column=2, rowspan=2, padx=8, pady=6)
        ttk.Button(btns, text="Frissítés", command=self.refresh_devices).pack(fill="x", pady=2)
        self.connect_btn = ttk.Button(btns, text="Csatlakozás", command=self.toggle_connect, style="Accent.TButton")
        self.connect_btn.pack(fill="x", pady=2)

        conn.columnconfigure(1, weight=1)

        play = ttk.LabelFrame(self.root, text="Lejátszás")
        play.pack(fill="x", **pad)

        ttk.Label(play, text="Hangszer").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        names = [pretty_instrument(n) for n in config.INSTRUMENTS]
        self.instrument_combo = ttk.Combobox(play, textvariable=self.instrument_var, values=names, state="readonly", width=32)
        self.instrument_combo.grid(row=0, column=1, sticky="w", padx=4, pady=6)
        self.instrument_combo.current(0)
        self.instrument_combo.bind("<<ComboboxSelected>>", self.on_instrument_change)

        ttk.Label(play, text="Hangerő").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Scale(play, from_=1, to=127, variable=self.velocity_var, orient="horizontal", length=120).grid(
            row=0, column=3, sticky="ew", padx=4, pady=6
        )
        ttk.Label(play, text="Duplázás").grid(row=0, column=4, sticky="w", padx=(12, 4), pady=6)
        self.doubling_combo = ttk.Combobox(
            play, textvariable=self.doubling_var, values=list(doubling.LABELS.values()), state="readonly", width=10
        )
        self.doubling_combo.grid(row=0, column=5, sticky="w", padx=(0, 8), pady=6)
        self.doubling_combo.bind("<<ComboboxSelected>>", self.on_doubling_change)

        actions = ttk.Frame(play)
        actions.grid(row=1, column=0, columnspan=6, sticky="w", padx=8, pady=(0, 8))
        ttk.Button(actions, text="C-dúr skála", command=self.play_scale).pack(side="left", padx=3)
        ttk.Button(actions, text="C-dúr akkord", command=self.play_chord).pack(side="left", padx=3)
        ttk.Button(actions, text="Bemutató", command=self.play_demo).pack(side="left", padx=3)
        ttk.Button(actions, text="Felvétel lejátszása…", command=self.open_record_file).pack(side="left", padx=3)
        ttk.Button(actions, text="Leállítás", command=self.stop_playback).pack(side="left", padx=3)
        ttk.Button(actions, text="Minden hang ki", command=self.panic).pack(side="left", padx=3)

        # Lejátszó sáv: betöltött felvétel vezérlése
        bar = ttk.Frame(play)
        bar.grid(row=2, column=0, columnspan=6, sticky="ew", padx=8, pady=(0, 8))
        self.player_btn = ttk.Button(bar, text="▶", width=3, command=self.player_play_pause)
        self.player_btn.pack(side="left")
        self.player_stop_btn = ttk.Button(bar, text="■", width=3, command=self.player_stop)
        self.player_stop_btn.pack(side="left", padx=(3, 8))
        ttk.Label(bar, textvariable=self.player_name_var, width=22, anchor="w").pack(side="left")
        self.position_scale = ttk.Scale(bar, from_=0, to=1, orient="horizontal", variable=self.player_pos_var)
        self.position_scale.pack(side="left", fill="x", expand=True, padx=8)
        self.position_scale.bind("<ButtonPress-1>", self._on_seek_press)
        self.position_scale.bind("<B1-Motion>", self._on_seek_drag)
        self.position_scale.bind("<ButtonRelease-1>", self._on_seek_release)
        ttk.Label(bar, textvariable=self.player_time_var, style="Status.TLabel").pack(side="left", padx=(0, 8))
        self.speed_combo = ttk.Combobox(
            bar, textvariable=self.speed_var, values=[speed_label(s) for s in playback.SPEEDS], state="readonly", width=6
        )
        self.speed_combo.pack(side="left")
        self.speed_combo.bind("<<ComboboxSelected>>", self.on_speed_change)

        play.columnconfigure(3, weight=1)

        piano_frame = ttk.LabelFrame(self.root, text="Zongora — 88 billentyű (egérrel vagy billentyűzettel)")
        piano_frame.pack(fill="x", **pad)
        octave_row = ttk.Frame(piano_frame)
        octave_row.pack(fill="x", padx=8, pady=(6, 0))
        ttk.Button(octave_row, text="◀ Oktáv (X)", command=lambda: self.shift_octave(-1)).pack(side="left")
        ttk.Label(octave_row, textvariable=self.kb_range_var, width=20, anchor="center").pack(side="left", padx=6)
        ttk.Button(octave_row, text="Oktáv (C) ▶", command=lambda: self.shift_octave(1)).pack(side="left")
        ttk.Checkbutton(
            octave_row, text="Betűk a billentyűkön", variable=self.show_letters_var, command=self.draw_piano
        ).pack(side="left", padx=12)
        ttk.Checkbutton(
            octave_row, text="Pedál (Szóköz)", variable=self.pedal_var, style="Pedal.TCheckbutton",
            command=lambda: self.set_pedal(self.pedal_var.get()),
        ).pack(side="left")
        ttk.Checkbutton(octave_row, text="Effekt", variable=self.fx_enabled_var, command=self.on_fx_toggle).pack(
            side="left", padx=12
        )
        self.fx_canvas = tk.Canvas(piano_frame, height=FX_HEIGHT, bg=self.palette["piano_bg"], highlightthickness=0)
        if self.fx_enabled_var.get():
            self.fx_canvas.pack(fill="x", padx=8, pady=(6, 0))
        self.fx_canvas.bind("<Configure>", lambda _e: self.draw_fx_floor())
        self.canvas = tk.Canvas(piano_frame, height=PIANO_HEIGHT, bg=self.palette["piano_bg"], highlightthickness=0)
        self.canvas.pack(fill="x", padx=8, pady=(0, 8) if self.fx_enabled_var.get() else 8)
        self.canvas.bind("<ButtonPress-1>", self.on_piano_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_piano_release)
        self.canvas.bind("<Leave>", self.on_piano_release)
        self.canvas.bind("<Configure>", lambda _e: self.draw_piano())

        listen = ttk.LabelFrame(self.root, text="Billentyűzet figyelése")
        listen.pack(fill="both", expand=True, **pad)
        toolbar = ttk.Frame(listen)
        toolbar.pack(fill="x", padx=8, pady=6)
        self.listen_btn = ttk.Button(toolbar, text="Figyelés indítása", command=self.toggle_listen)
        self.listen_btn.pack(side="left")
        self.record_btn = ttk.Button(toolbar, text="● Felvétel", command=self.toggle_record)
        self.record_btn.pack(side="left", padx=(8, 3))
        ttk.Button(toolbar, text="Felvételek…", command=self.open_records).pack(side="left", padx=3)
        ttk.Label(toolbar, textvariable=self.record_var, style="Status.TLabel").pack(side="left", padx=8)

        self.log = tk.Text(listen, height=4, wrap="word", state="disabled")  # a maradék helyet kitölti
        scroll = ttk.Scrollbar(listen, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=(0, 8))

        # az állapotsor elsőként kap helyet (alul), így kis ablakban sem szorul ki
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel")
        self.status_label.pack(side="bottom", fill="x", padx=12, pady=(0, 10), before=self.header)

        self.sections = [(frame, frame.cget("text")) for frame in (conn, play, piano_frame, listen)]

    # --- téma -------------------------------------------------------------

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

    def log_line(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def refresh_devices(self):
        inputs, outputs = self.controller.list_devices()
        self.input_combo["values"] = inputs or [""]
        self.output_combo["values"] = outputs or [""]
        if inputs:
            self.input_var.set(self._preferred(inputs) or inputs[0])
        else:
            self.input_var.set("")
        if outputs:
            self.output_var.set(self._preferred(outputs) or outputs[0])
        else:
            self.output_var.set("")
        self.log_line(f"Eszközök: {len(inputs)} bemenet, {len(outputs)} kimenet")

    def _preferred(self, names):
        for name in names:
            if any(k.upper() in name.upper() for k in config.DEVICE_NAME_KEYWORDS):
                return name
        return None

    def toggle_connect(self):
        if self.controller.connected:
            self._finish_recording()
            self.stop_playback()
            self.stop_listen()
            self.controller.close()
            self.connect_btn.configure(text="Csatlakozás")
            self.log_line("Kapcsolat bontva")
            self._activate_output("Kapcsolat bontva")
            return

        inp = self.input_var.get().strip() or None
        out = self.output_var.get().strip() or None
        if not inp and not out:
            messagebox.showwarning("Nincs eszköz", "Válassz MIDI bemenetet vagy kimenetet.")
            return

        ok = self.controller.connect(input_name=inp, output_name=out)
        if not ok:
            messagebox.showerror("Hiba", "Nem sikerült csatlakozni a MIDI eszközhöz.")
            self._activate_output("Csatlakozás sikertelen")
            return

        self.connect_btn.configure(text="Leválasztás")
        self.log_line(f"Csatlakozva — be: {inp or '-'} / ki: {out or '-'}")
        self._activate_output()

    def _activate_output(self, idle_text: str = "Nincs csatlakozás"):
        """Az aktív hangkimenet kiírása az állapotsorba és a hangszer beállítása rajta."""
        c = self.controller
        head = f"Csatlakozva: {c.device_name}" if c.connected else idle_text
        name = c.output_name
        if name is None:
            self.base_status = f"{head} — nincs hangkimenet"
        elif c.using_fallback:
            self.base_status = f"{head} — hang: {name} (alapértelmezett)"
        else:
            self.base_status = head
        self.status_var.set(self.base_status)
        if c.fallback_error and not self.fallback_error_logged:
            self.fallback_error_logged = True
            self.log_line(c.fallback_error)
        self.on_instrument_change()

    def require_output(self) -> bool:
        if self.controller.active_output is not None:
            return True
        messagebox.showinfo("Nincs hangkimenet", "Nincs elérhető hangkimenet. Csatlakozz egy MIDI kimenethez.")
        return False

    def on_instrument_change(self, _event=None):
        if self.controller.active_output is None:
            return
        label = self.instrument_var.get()
        for name, num in config.INSTRUMENTS.items():
            if pretty_instrument(name) == label:
                self.controller.change_instrument(num)
                self.log_line(f"Hangszer: {label}")
                return

    def play_scale(self):
        self._play_sequence(C_MAJOR_SCALE, hold_ms=280, gap_ms=80, label="C-dúr skála")

    def play_demo(self):
        self._play_sequence(DEMO_MELODY, hold_ms=180, gap_ms=40, label="Bemutató")

    def play_chord(self):
        if not self.require_output():
            return
        self.stop_playback(quiet=True)
        self.playing = True
        vel = int(self.velocity_var.get())
        for note in C_MAJOR_CHORD:
            self.controller.note_on(note, vel)
            self.highlight(note, True, vel)
        self.log_line("C-dúr akkord")
        self.play_job = self.root.after(1600, lambda: self._end_chord(C_MAJOR_CHORD))

    def _end_chord(self, notes):
        for note in notes:
            self.controller.note_off(note)
            self.highlight(note, False)
        self.playing = False
        self.play_job = None

    def _play_sequence(self, notes, hold_ms, gap_ms, label):
        if not self.require_output():
            return
        self.stop_playback(quiet=True)
        self.playing = True
        self.log_line(label)
        self._play_index(notes, 0, hold_ms, gap_ms)

    def _play_index(self, notes, index, hold_ms, gap_ms):
        if not self.playing:
            return
        if index >= len(notes):
            self.playing = False
            self.play_job = None
            return
        note = notes[index]
        vel = int(self.velocity_var.get())
        self.controller.note_on(note, vel)
        self.highlight(note, True, vel)
        self.play_job = self.root.after(hold_ms, lambda: self._release_then_next(notes, index, hold_ms, gap_ms))

    def _release_then_next(self, notes, index, hold_ms, gap_ms):
        note = notes[index]
        self.controller.note_off(note)
        self.highlight(note, False)
        if not self.playing:
            return
        self.play_job = self.root.after(gap_ms, lambda: self._play_index(notes, index + 1, hold_ms, gap_ms))

    def stop_playback(self, quiet: bool = False):
        """Minden lejátszás (skála / akkord / bemutató / felvétel) leállítása."""
        self.playing = False
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None
        self.panic(quiet)

    def panic(self, quiet: bool = False):
        was_active = self.player.is_playing or self.player.is_paused
        self.player.stop()
        self.set_pedal(False)
        self.controller.panic()
        for note in list(self.active_notes):
            self.highlight(note, False)
        self.active_notes.clear()
        if was_active:
            self.status_var.set(self.base_status)
        self._refresh_player_ui()
        if quiet:
            return
        if was_active:
            self.log_line(f"Lejátszás leállítva: {self.player.record_name}")
        self.log_line("Minden hang leállítva")

    def _stop_sequences(self):
        """Skála / akkord / bemutató leállítása a betöltött felvétel érintése nélkül."""
        if not self.playing and not self.play_job:
            return
        self.playing = False
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None
        self.controller.panic()
        for note in list(self.active_notes):
            self.highlight(note, False)

    # --- felvétel visszajátszása ------------------------------------------

    def open_record_file(self):
        folder = recorder.RECORDS_DIR if recorder.RECORDS_DIR.is_dir() else recorder.RECORDS_DIR.parent
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Felvétel megnyitása",
            initialdir=str(folder),
            filetypes=[("Felvételek", "*.json"), ("Minden fájl", "*.*")],
        )
        if path:
            self.play_record_file(path)

    def play_record_file(self, path, parent=None):
        """Felvétel betöltése és lejátszása; a hangszere lesz az alapértelmezett (átállítható)."""
        path = Path(path)
        try:
            record = recorder.load_record(path)
        except ValueError as e:
            messagebox.showerror("Hibás felvétel", f"{path.name}\n\n{e}", parent=parent or self.root)
            return
        if not self.require_output():
            return
        self.stop_playback(quiet=True)
        instrument = playback.default_instrument(record, config.INSTRUMENTS)
        self.instrument_var.set(pretty_instrument(instrument))
        self.on_instrument_change()
        if not record["notes"]:
            messagebox.showinfo("Üres felvétel", f"A(z) „{path.stem}” felvételben nincs hang.", parent=parent or self.root)
            return
        self.player.set_speed(float(self.speed_var.get().rstrip("x")))
        self.player.play(record, path.stem)
        self.log_line(
            f"Lejátszás: {path.stem} ({len(record['notes'])} hang, {format_seconds(self.player.duration)})"
        )
        self._player_changed()

    def _on_player_note(self, note: int, velocity: int, on: bool):
        if on:
            self.controller.note_on(note, velocity)
        else:
            self.controller.note_off(note)
        self.highlight(note, on, velocity)

    def _on_player_finish(self):
        self.log_line(f"Lejátszás vége: {self.player.record_name}")
        self._player_changed()

    # --- lejátszó sáv -----------------------------------------------------

    def player_play_pause(self):
        if not self.player.is_loaded:
            return
        if not self.player.is_playing:
            if not self.require_output():
                return
            self._stop_sequences()
        self.player.play_pause()
        self._player_changed()

    def player_stop(self):
        if not self.player.is_loaded:
            return
        self.player.stop()
        self._player_changed()

    def on_speed_change(self, _event=None):
        self.player.set_speed(float(self.speed_var.get().rstrip("x")))
        self._player_changed()

    def _player_changed(self):
        """Állapotsor + lejátszó sáv frissítése egy lejátszó művelet után."""
        name = self.player.record_name
        if self.player.is_playing:
            self.status_var.set(f"Lejátszás: {name} ({self.speed_var.get()})")
        elif self.player.is_paused:
            self.status_var.set(f"Szünet: {name}")
        else:
            self.status_var.set(self.base_status)
        self._refresh_player_ui()

    def _refresh_player_ui(self):
        if self.player_ui_job:
            self.root.after_cancel(self.player_ui_job)
            self.player_ui_job = None
        p = self.player
        state = ["!disabled"] if p.is_loaded else ["disabled"]
        for widget in (self.player_btn, self.player_stop_btn, self.position_scale):
            widget.state(state)
        self.player_btn.configure(text="⏸" if p.is_playing else "▶")
        self.player_name_var.set(p.record_name or "Nincs betöltött felvétel")
        duration = p.duration
        self.position_scale.configure(to=max(duration, 0.001))
        position = self.player_pos_var.get() if self.seeking else p.position()
        if not self.seeking:
            self.player_pos_var.set(position)
        self.player_time_var.set(f"{format_seconds(position)} / {format_seconds(duration)}")
        if p.is_playing:
            self.player_ui_job = self.root.after(PLAYER_TICK_MS, self._refresh_player_ui)

    def _seek_value(self, event) -> float:
        width = max(self.position_scale.winfo_width() - 2 * SEEK_MARGIN, 1)
        fraction = min(max((event.x - SEEK_MARGIN) / width, 0.0), 1.0)
        return fraction * self.player.duration

    def _on_seek_press(self, event):
        if self.player.is_loaded:
            self.seeking = True
            self.player_pos_var.set(self._seek_value(event))
            self._refresh_player_ui()
        return "break"

    def _on_seek_drag(self, event):
        if self.seeking:
            self.player_pos_var.set(self._seek_value(event))
            self._refresh_player_ui()
        return "break"

    def _on_seek_release(self, event):
        if self.seeking:
            self.seeking = False
            self.player.seek(self._seek_value(event))
            self._player_changed()
        return "break"

    def toggle_listen(self):
        if self.listening:
            self.stop_listen()
            return
        if not self.controller.connected or not self.controller.input_port:
            messagebox.showinfo("Nincs bemenet", "Előbb csatlakozz egy MIDI bemenethez.")
            return
        self.listening = True
        self.listen_btn.configure(text="Figyelés leállítása")
        self.log_line("Figyelés indítva — játssz a zongorán")
        self.poll_midi()

    def stop_listen(self):
        self.listening = False
        if self.listen_job:
            self.root.after_cancel(self.listen_job)
            self.listen_job = None
        self.listen_btn.configure(text="Figyelés indítása")

    def poll_midi(self):
        if not self.listening or not self.controller.input_port:
            return
        try:
            for msg in self.controller.input_port.iter_pending():
                if msg.type in ("note_on", "note_off"):
                    on = msg.type == "note_on" and msg.velocity > 0
                    action = "ON " if on else "OFF"
                    self.log_line(f"{action} {note_label(msg.note)} ({msg.note}) hangerő {msg.velocity}")
                    self.highlight(msg.note, on, msg.velocity)
                    if on:
                        self.recorder.note_on(msg.note, msg.velocity)
                    else:
                        self.recorder.note_off(msg.note)
                elif msg.type == "control_change":
                    self.log_line(f"CC {msg.control} -> {msg.value}")
                elif msg.type == "program_change":
                    self.log_line(f"PC -> {msg.program}")
                else:
                    self.log_line(str(msg))
        except Exception as e:
            self.log_line(f"Olvasási hiba: {e}")
            self.stop_listen()
            return
        self.listen_job = self.root.after(15, self.poll_midi)

    def draw_piano(self):
        p = self.palette
        self.canvas.delete("all")
        self.key_ids.clear()
        width = max(self.canvas.winfo_width(), 100)
        height = PIANO_HEIGHT
        labels = set(piano_layout.label_notes())
        for key in piano_layout.layout(width, height):
            if key.black:
                color = p["key_black_active"] if key.note in self.active_notes else p["key_black"]
            else:
                color = p["key_white_active"] if key.note in self.active_notes else p["key_white"]
            kid = self.canvas.create_rectangle(
                key.x0, key.y0, key.x1, key.y1, fill=color, outline=p["key_outline"], width=1,
                tags=("key", f"n{key.note}"),
            )
            self.key_ids[key.note] = kid
            if key.note in labels:
                cx = (key.x0 + key.x1) / 2
                middle = key.note == piano_layout.MIDDLE_C
                self.canvas.create_text(
                    cx, height - 12, text=note_label(key.note), fill=p["accent"] if middle else p["key_label"],
                    font=(self.font_family, 7, "bold" if middle else "normal"), state="disabled",
                )
                if middle:
                    self.canvas.create_oval(cx - 3, height - 30, cx + 3, height - 24, fill=p["accent"], outline="",
                                            state="disabled")
        self._draw_keyboard_range(width, height)

    def _draw_keyboard_range(self, width, height):
        """A számítógép-billentyűzettel elérhető tartomány: sáv felül + betűk (ha be van kapcsolva)."""
        p = self.palette
        low, high = self.keyboard.range_notes()
        keys = {k.note: k for k in piano_layout.layout(width, height)}
        x0 = min(keys[n].x0 for n in range(low, high + 1))
        x1 = max(keys[n].x1 for n in range(low, high + 1))
        # naplemente színátmenet a tartomány sávon (a világos / sötét témában ez az akcentus árnyalatai)
        segments = 24
        for i in range(segments):
            t = i / (segments - 1)
            color = theme.mix(p["sun_top"], p["sun_mid"], t * 2) if t < 0.5 else theme.mix(p["sun_mid"], p["sun_bottom"], t * 2 - 1)
            sx0 = x0 + (x1 - x0) * i / segments
            sx1 = x0 + (x1 - x0) * (i + 1) / segments + 1
            self.canvas.create_rectangle(sx0, 0, sx1, 4, fill=color, outline="", state="disabled", tags=("range",))
        if not self.show_letters_var.get():
            return
        for note, letter in self.keyboard.key_labels().items():
            key = keys[note]
            cx = (key.x0 + key.x1) / 2
            if key.black:
                y, color = key.y1 - 9, p["key_white"]
            else:
                y, color = height - 44, p["accent"]
            self.canvas.create_text(cx, y, text=letter, fill=color, font=(self.font_family, 7, "bold"),
                                    state="disabled", tags=("letter",))

    def shift_octave(self, octaves: int):
        if not self.keyboard.shift(octaves):
            self.log_line("A billentyűzet tartománya elérte a zongora szélét")

    def _on_keyboard_range(self):
        low, high = self.keyboard.range_notes()
        self.kb_range_var.set(f"Billentyűzet: {note_label(low)}–{note_label(high)}")
        self.draw_piano()

    def note_from_event(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in reversed(items):
            for tag in self.canvas.gettags(item):
                if tag.startswith("n") and tag[1:].isdigit():
                    return int(tag[1:])
        return None

    def on_piano_press(self, event):
        note = self.note_from_event(event)
        if note is None or note in self.held_notes:
            return
        if self._user_note_on(note):
            self.held_notes.add(note)
            self.log_line(f"ON  {note_label(note)} ({note})")

    def on_piano_release(self, _event=None):
        if not self.held_notes:
            return
        for note in list(self.held_notes):
            self._user_note_off(note)
        self.held_notes.clear()

    def _user_note_on(self, note: int) -> bool:
        """Egérrel / billentyűzettel játszott hang: kimenet, felvétel, kiemelés. False, ha nem szól és nem is rögzül."""
        audible = self.controller.active_output is not None
        if not audible and not self.recorder.is_recording:
            return False
        velocity = int(self.velocity_var.get())
        for n in self.doubler.press(note):  # a hang + az oktáv duplázás hangjai
            self.pedal.key_down(n)
            if audible:
                self.controller.note_on(n, velocity)
            self.recorder.note_on(n, velocity)
            self.highlight(n, True, velocity)
        return True

    def _user_note_off(self, note: int):
        """Billentyű elengedve: lenyomott pedálnál a hang tovább szól; közös hang addig szól, amíg kell."""
        for n in self.doubler.release(note):
            if self.pedal.key_up(n):
                self._stop_note(n)

    def on_doubling_change(self, _event=None):
        label = self.doubling_var.get()
        mode = next((m for m, text in doubling.LABELS.items() if text == label), doubling.DEFAULT_MODE)
        self.doubler.set_mode(mode)
        theme.save_setting("octave_doubling", mode)
        self.log_line(f"Oktáv duplázás: {label}")

    def _stop_note(self, note: int):
        self.controller.note_off(note)
        self.recorder.note_off(note)
        self.highlight(note, False)

    # --- kitartó pedál ------------------------------------------------------

    def set_pedal(self, down: bool):
        if down == self.pedal.down:
            self.pedal_var.set(down)
            return
        if down:
            self.pedal.press()
            self.controller.sustain(True)
        else:
            self.controller.sustain(False)
            self.pedal.release()
        self.pedal_var.set(down)

    def _on_space(self, event, down: bool):
        """Szóköz a főablak gombjain is pedál; a párbeszédablakokban marad a szokásos gombnyomás."""
        if event.widget.winfo_toplevel() is not self.root:
            if down:
                event.widget.invoke()
            return "break"
        if down:
            self.keyboard.press("space")
        else:
            self.keyboard.release("space")
        return "break"

    # --- számítógép billentyűzet --------------------------------------------

    TEXT_INPUT_CLASSES = ("Entry", "TEntry", "TCombobox", "Spinbox", "TSpinbox")
    MODIFIER_MASK = 0x0004 | 0x0008 | 0x20000  # Control, Mod1 (Alt X11-en), Alt (Windows)

    def _bind_keyboard(self):
        self._on_keyboard_range()
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<FocusOut>", self._on_focus_out)
        for cls in ("TButton", "TCheckbutton"):
            self.root.bind_class(cls, "<KeyPress-space>", lambda e: self._on_space(e, True))
            self.root.bind_class(cls, "<KeyRelease-space>", lambda e: self._on_space(e, False))
        # választás után a fókusz visszakerül az ablakra, hogy a billentyűzet újra zongorázzon
        for combo in (self.input_combo, self.output_combo, self.theme_combo, self.instrument_combo, self.speed_combo,
                      self.doubling_combo):
            combo.bind("<<ComboboxSelected>>", lambda _e: self.root.focus_set(), add="+")

    def _is_text_input(self, widget) -> bool:
        try:
            return widget.winfo_class() in self.TEXT_INPUT_CLASSES
        except (AttributeError, tk.TclError):
            return False

    def on_key_press(self, event):
        if event.state & self.MODIFIER_MASK or self._is_text_input(event.widget):
            return None
        if self.keyboard.press(event.keysym):
            return "break"
        return None

    def on_key_release(self, event):
        if self.keyboard.release(event.keysym):
            return "break"
        return None

    def _on_keyboard_note(self, note: int, on: bool):
        if on:
            self._user_note_on(note)
        else:
            self._user_note_off(note)

    def _on_focus_out(self, _event=None):
        # a fókusz ablakon belüli váltásakor is jön FocusOut — csak ha tényleg elhagyta az ablakot
        self.root.after_idle(self._release_if_unfocused)

    def _release_if_unfocused(self):
        try:
            focused = self.root.focus_get()
        except (KeyError, tk.TclError):
            focused = None
        if focused is None or focused.winfo_toplevel() is not self.root:
            self.keyboard.release_all()
            self.set_pedal(False)

    def highlight(self, note: int, on: bool, velocity: int = 100):
        """Billentyű kiemelése — minden hangforrás (egér, billentyűzet, MIDI bemenet, lejátszás, bemutató) ezen át megy,
        így a vizualizáció is innen kapja a hangokat."""
        if on:
            self.active_notes.add(note)
        else:
            self.active_notes.discard(note)
        if self.fx_enabled_var.get() and piano_layout.FIRST_NOTE <= note <= piano_layout.LAST_NOTE:
            if on:
                self.visualizer.note_on(note, velocity)
            else:
                self.visualizer.note_off(note)
            self._start_fx()
        kid = self.key_ids.get(note)
        if not kid:
            return
        is_black = piano_layout.is_black(note)
        p = self.palette
        if on:
            self.canvas.itemconfigure(kid, fill=p["key_black_active"] if is_black else p["key_white_active"])
        else:
            self.canvas.itemconfigure(kid, fill=p["key_black"] if is_black else p["key_white"])

    # --- hangvizualizáció -------------------------------------------------

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
        line = theme.mix(p["piano_bg"], p["grid"], 0.28 if self.scheme == theme.SYNTHWAVE_MODE else 0.18)
        for k in range(1, 6):
            y = height * (k / 6) ** 1.6
            c.create_line(0, y, width, y, fill=line, tags=("floor",))
        vx = width / 2
        for i in range(-16, 17):
            c.create_line(vx + i * width / 50, 0, vx + i * width / 14, height, fill=line, tags=("floor",))
        c.tag_lower("floor")

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

    # --- felvétel ---------------------------------------------------------

    def _current_instrument(self):
        label = self.instrument_var.get()
        for name, num in config.INSTRUMENTS.items():
            if pretty_instrument(name) == label:
                return name, num
        return next(iter(config.INSTRUMENTS.items()))

    def toggle_record(self):
        if self.recorder.is_recording:
            self._finish_recording()
            return
        name, program = self._current_instrument()
        self.recorder.start(name, program)
        self.record_btn.configure(text="■ Leállítás", style="Accent.TButton")
        if self.controller.connected and self.controller.input_port:
            if not self.listening:
                self.toggle_listen()
            self.log_line(f"Felvétel indítva ({pretty_instrument(name)})")
        else:
            self.log_line("Felvétel indítva kapcsolat nélkül — a képernyős zongora hangjai rögzülnek")
        self._tick_recording()

    def _tick_recording(self):
        self.record_job = None
        if not self.recorder.is_recording:
            return
        self.record_var.set(f"● {format_seconds(self.recorder.elapsed())} · {self.recorder.note_count} hang")
        self.record_job = self.root.after(RECORD_TICK_MS, self._tick_recording)

    def _finish_recording(self):
        """Felvétel leállítása, majd mentés / elvetés párbeszéd (üres felvételnél nincs)."""
        if not self.recorder.is_recording:
            return
        record = self.recorder.stop()
        if self.record_job:
            self.root.after_cancel(self.record_job)
            self.record_job = None
        self.record_btn.configure(text="● Felvétel", style="TButton")
        self.record_var.set("")
        if not record["notes"]:
            self.log_line("Üres felvétel, nem mentve")
            return
        self._ask_save(record)

    def _ask_save(self, record: dict):
        """Modális ablak: név megadása (alapértelmezett: felvetel_YYYYMMDD_HHMMSS), Mentés vagy Elvetés."""
        dlg = tk.Toplevel(self.root)
        self.save_dialog = dlg
        dlg.title("Felvétel mentése")
        dlg.configure(bg=self.palette["bg"])
        dlg.resizable(False, False)
        dlg.transient(self.root)

        body = ttk.Frame(dlg, padding=14)
        body.pack(fill="both", expand=True)
        summary = (
            f"{len(record['notes'])} hang · {format_seconds(record['duration'])} · "
            f"{pretty_instrument(record['instrument']['name'])}"
        )
        ttk.Label(body, text=summary, style="Status.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(body, text="Név").grid(row=1, column=0, sticky="w", padx=(0, 8))
        name_var = tk.StringVar(value=recorder.default_name())
        entry = ttk.Entry(body, textvariable=name_var, width=38)
        entry.grid(row=1, column=1, sticky="ew")
        ttk.Label(body, text=f"Mentés helye: {recorder.RECORDS_DIR}", style="Status.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(6, 10)
        )

        def save(_event=None):
            try:
                try:
                    path = recorder.save_record(record, name_var.get())
                except FileExistsError as e:
                    if not messagebox.askyesno("Már létezik", f"A(z) „{e.args[0].name}” már létezik. Felülírod?", parent=dlg):
                        return
                    path = recorder.save_record(record, name_var.get(), overwrite=True)
            except ValueError as e:
                messagebox.showerror("Hibás név", str(e), parent=dlg)
                return
            except OSError as e:
                messagebox.showerror("Mentési hiba", f"Nem sikerült menteni: {e}", parent=dlg)
                return
            self.log_line(f"Felvétel mentve: {path}")
            self.status_var.set(f"Felvétel mentve: {path.name}")
            dlg.destroy()
            self.refresh_records()

        def discard(_event=None):
            if messagebox.askyesno("Elvetés", "Biztosan elveted a felvételt? Nem lesz mentve.", parent=dlg):
                self.log_line("Felvétel elvetve")
                dlg.destroy()

        btns = ttk.Frame(body)
        btns.grid(row=3, column=0, columnspan=2, sticky="e")
        ttk.Button(btns, text="Elvetés", command=discard).pack(side="left", padx=3)
        ttk.Button(btns, text="Mentés", command=save, style="Accent.TButton").pack(side="left", padx=3)
        body.columnconfigure(1, weight=1)

        dlg.protocol("WM_DELETE_WINDOW", discard)
        dlg.bind("<Return>", save)
        dlg.bind("<Escape>", discard)
        entry.focus_set()
        entry.select_range(0, "end")
        dlg.grab_set()
        self.root.wait_window(dlg)
        self.save_dialog = None

    # --- felvételek listája -----------------------------------------------

    def open_records(self):
        if self.records_win is not None and self.records_win.winfo_exists():
            self.records_win.deiconify()
            self.records_win.lift()
            self.refresh_records()
            return
        win = tk.Toplevel(self.root)
        self.records_win = win
        win.title("Felvételek")
        win.geometry("720x380")
        win.minsize(520, 260)
        win.configure(bg=self.palette["bg"])

        body = ttk.Frame(win, padding=10)
        body.pack(fill="both", expand=True)

        columns = ("name", "created", "duration", "notes", "instrument")
        headings = ("Név", "Létrehozva", "Hossz", "Hangok", "Hangszer")
        widths = (200, 140, 60, 60, 180)
        tree = ttk.Treeview(body, columns=columns, show="headings", selectmode="extended")
        for col, text, width in zip(columns, headings, widths):
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor="e" if col in ("duration", "notes") else "w")
        tree.tag_configure("error", foreground=self.palette["muted"])
        self.records_tree = tree
        scroll = ttk.Scrollbar(body, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.grid(row=0, column=0, sticky="nsew")
        scroll.grid(row=0, column=1, sticky="ns")

        btns = ttk.Frame(body)
        btns.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(btns, text="Lejátszás", command=self.play_selected_record, style="Accent.TButton").pack(
            side="left", padx=(0, 3)
        )
        ttk.Button(btns, text="Összes kijelölése", command=self.select_all_records).pack(side="left", padx=3)
        ttk.Button(btns, text="Törlés", command=self.delete_selected_records).pack(side="left", padx=3)
        ttk.Button(btns, text="Frissítés", command=self.refresh_records).pack(side="left", padx=3)
        ttk.Button(btns, text="Mappa megnyitása", command=self.open_records_folder).pack(side="left", padx=3)
        ttk.Button(btns, text="Bezárás", command=win.destroy).pack(side="right")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        tree.bind("<Double-1>", lambda e: self.play_selected_record() if tree.identify_row(e.y) else None)
        tree.bind("<Return>", lambda _e: self.play_selected_record())
        tree.bind("<Delete>", lambda _e: self.delete_selected_records())
        tree.bind("<Control-a>", lambda _e: self.select_all_records())
        win.bind("<Escape>", lambda _e: win.destroy())
        win.bind("<Destroy>", self._on_records_destroy)
        self.refresh_records()
        tree.focus_set()

    def _on_records_destroy(self, event):
        if event.widget is self.records_win:
            self.records_win = None
            self.records_tree = None

    def refresh_records(self):
        tree = self.records_tree
        if tree is None:
            return
        tree.delete(*tree.get_children())
        for info in recorder.list_records():
            if info.error:
                values = (info.name, "—", "—", "—", f"hibás: {info.error}")
                tree.insert("", "end", iid=str(info.path), values=values, tags=("error",))
            else:
                values = (
                    info.name,
                    info.created.replace("T", " "),
                    format_seconds(info.duration),
                    info.note_count,
                    pretty_instrument(info.instrument),
                )
                tree.insert("", "end", iid=str(info.path), values=values)

    def play_selected_record(self):
        tree = self.records_tree
        if tree is None:
            return
        selected = tree.selection()
        if len(selected) != 1:
            messagebox.showinfo(
                "Válassz egy felvételt", "A lejátszáshoz pontosan egy felvételt jelölj ki.", parent=self.records_win
            )
            return
        self.play_record_file(selected[0], parent=self.records_win)

    def select_all_records(self):
        if self.records_tree is not None:
            self.records_tree.selection_set(self.records_tree.get_children())
        return "break"

    def delete_selected_records(self):
        tree = self.records_tree
        if tree is None:
            return
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Nincs kijelölés", "Jelölj ki egy vagy több felvételt a törléshez.", parent=self.records_win)
            return
        if len(selected) == 1:
            question = f"Biztosan törlöd a(z) „{tree.set(selected[0], 'name')}” felvételt?"
        else:
            question = f"Biztosan törlöd a kijelölt {len(selected)} felvételt?"
        if not messagebox.askyesno("Törlés", question, parent=self.records_win):
            return
        try:
            count = recorder.delete_records(selected)
        except (ValueError, OSError) as e:
            messagebox.showerror("Törlési hiba", str(e), parent=self.records_win)
            count = 0
        self.log_line(f"{count} felvétel törölve")
        self.refresh_records()

    def open_records_folder(self):
        folder = recorder.RECORDS_DIR
        try:
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform.startswith("win"):
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(folder)])
            else:
                subprocess.Popen(["xdg-open", str(folder)])
        except OSError as e:
            messagebox.showerror("Hiba", f"A mappa nem nyitható meg: {e}", parent=self.records_win)

    def on_close(self):
        self.keyboard.release_all()
        self.set_pedal(False)
        self._finish_recording()
        if self.fx_job:
            self.root.after_cancel(self.fx_job)
            self.fx_job = None
        if self.theme_job:
            self.root.after_cancel(self.theme_job)
            self.theme_job = None
        self.stop_playback()
        self.stop_listen()
        self.controller.shutdown()
        self.root.destroy()


def run():
    root = tk.Tk()
    PianoApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
