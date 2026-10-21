"""A főablak: összerakja a felület részeit (mixinek) és kezeli az életciklust."""

import tkinter as tk
from tkinter import ttk

from synth_mido import config
from synth_mido.audio.midi_controller import VevorMIDIController
from synth_mido.core import doubling, events, keyboard_play, playback, recorder
from synth_mido.core.sustain import SustainPedal
from synth_mido.fx.visualizer import Visualizer
from synth_mido.skins import registry, theme
from synth_mido.ui.common import (
    FX_HEIGHT,
    HEADER_HEIGHT,
    PIANO_HEIGHT,
    pretty_instrument,
    speed_label,
)
from synth_mido.ui.connection import ConnectionMixin
from synth_mido.ui.fx_view import FxMixin
from synth_mido.ui.input import InputMixin
from synth_mido.ui.piano_view import PianoViewMixin
from synth_mido.ui.playback_view import PlaybackMixin
from synth_mido.ui.recording import RecordingMixin
from synth_mido.ui.records_window import RecordsWindowMixin
from synth_mido.ui.theming import ThemingMixin


class PianoApp(ThemingMixin, ConnectionMixin, PlaybackMixin, PianoViewMixin, InputMixin, FxMixin, RecordingMixin, RecordsWindowMixin):
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VEVOR MIDI vezérlő")
        self.root.minsize(780, 800)
        self.root.geometry("860x940")

        self.controller = VevorMIDIController()
        self.listening = False
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

        self._init_skin()
        self.theme_job = None
        self.style = ttk.Style(self.root)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.instrument_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Nincs csatlakozás")
        self.velocity_var = tk.IntVar(value=100)
        self.skin_var = tk.StringVar(value=self.skin.name)
        self.variant_var = tk.StringVar(value=registry.VARIANT_LABELS[self.variant])
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
        # Observer: minden hang a NoteBus-on megy át; a nézetek feliratkoznak
        self.notes = events.NoteBus()
        self.notes.subscribe(self._paint_key)
        self.notes.subscribe(self._on_note_event)
        self.fx_enabled_var = tk.BooleanVar(value=bool(theme.load_setting("visual_fx", True)))
        self.fx_job = None
        self.eq_window = None  # Winamp-szerű hangszínszabályzó ablak (TASK-014)
        self._fx_keys = {}
        self._fx_pool = {"rect": [], "oval": []}
        self._fx_shown = {"rect": 0, "oval": 0}
        saved_doubling = theme.load_setting("octave_doubling", doubling.DEFAULT_MODE)
        self.doubler = doubling.OctaveDoubler(saved_doubling)
        self.doubling_var = tk.StringVar(value=doubling.LABELS[self.doubler.mode])
        self.octaves = doubling.OctaveSelection(self.keyboard.base)
        self.octave_label_var = tk.StringVar(value=f"Oktávok: {self.octaves.label()}")

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
        look = ttk.Frame(conn)
        look.grid(row=2, column=1, sticky="w", padx=4, pady=6)
        self.skin_combo = ttk.Combobox(
            look, textvariable=self.skin_var, values=[s.name for s in registry.all_skins()], state="readonly", width=16
        )
        self.skin_combo.pack(side="left")
        self.skin_combo.bind("<<ComboboxSelected>>", self.on_skin_change)
        self.variant_combo = ttk.Combobox(
            look, textvariable=self.variant_var, values=list(registry.VARIANT_LABELS.values()), state="readonly",
            width=10,
        )
        self.variant_combo.pack(side="left", padx=(6, 0))
        self.variant_combo.bind("<<ComboboxSelected>>", self.on_variant_change)

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
        self.instrument_combo = ttk.Combobox(play, textvariable=self.instrument_var, values=names, state="readonly", width=24)
        self.instrument_combo.grid(row=0, column=1, sticky="w", padx=4, pady=6)
        self.instrument_combo.current(0)
        self.instrument_combo.bind("<<ComboboxSelected>>", self.on_instrument_change)

        ttk.Label(play, text="Hangerő").grid(row=0, column=2, sticky="w", padx=8, pady=6)
        ttk.Scale(play, from_=1, to=127, variable=self.velocity_var, orient="horizontal", length=100).grid(
            row=0, column=3, sticky="ew", padx=4, pady=6
        )
        ttk.Label(play, text="Duplázás").grid(row=0, column=4, sticky="w", padx=(12, 4), pady=6)
        self.doubling_combo = ttk.Combobox(
            play, textvariable=self.doubling_var, values=list(doubling.LABELS.values()), state="readonly", width=10
        )
        self.doubling_combo.grid(row=0, column=5, sticky="w", padx=(0, 8), pady=6)
        self.doubling_combo.bind("<<ComboboxSelected>>", self.on_doubling_change)

        actions = self.actions_row = ttk.Frame(play)
        actions.grid(row=1, column=0, columnspan=6, sticky="w", padx=8, pady=(0, 8))
        ttk.Button(actions, text="Megnyitás…", command=self.open_record_file, style="Small.TButton").pack(side="left", padx=3)
        ttk.Button(actions, text="Leállítás", command=self.stop_playback, style="Small.TButton").pack(side="left", padx=3)

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
        octave_row = self.octave_row = ttk.Frame(piano_frame)
        octave_row.pack(fill="x", padx=8, pady=(6, 0))
        ttk.Button(octave_row, text="◀ Oktáv (X)", command=lambda: self.shift_octave(-1), style="Small.TButton").pack(side="left")
        ttk.Label(octave_row, textvariable=self.kb_range_var, width=8, anchor="center").pack(side="left", padx=6)
        ttk.Button(octave_row, text="Oktáv (C) ▶", command=lambda: self.shift_octave(1), style="Small.TButton").pack(side="left")
        ttk.Checkbutton(
            octave_row, text="Betűk", variable=self.show_letters_var, command=self.draw_piano
        ).pack(side="left", padx=12)
        ttk.Checkbutton(
            octave_row, text="Pedál (Szóköz)", variable=self.pedal_var, style="Pedal.TCheckbutton",
            command=lambda: self.set_pedal(self.pedal_var.get()),
        ).pack(side="left")
        ttk.Checkbutton(octave_row, text="Effekt", variable=self.fx_enabled_var, command=self.on_fx_toggle).pack(
            side="left", padx=12
        )
        # Oktávok (TASK-017): több oktáv egyszerre — a billentyűzet oktávja mindig be van jelölve
        self.octave_button = ttk.Menubutton(octave_row, textvariable=self.octave_label_var)
        self.octave_menu = tk.Menu(self.octave_button, tearoff=0)
        self.octave_vars = {}
        for base in doubling.OCTAVE_BASES:
            var = tk.BooleanVar(value=self.octaves.is_selected(base))
            self.octave_vars[base] = var
            self.octave_menu.add_checkbutton(label=doubling.octave_label(base), variable=var,
                                             command=lambda b=base: self.toggle_octave(b))
        self.octave_button["menu"] = self.octave_menu
        self.octave_button.pack(side="left")
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
        ttk.Button(toolbar, text="Equalizer…", command=self.open_equalizer).pack(side="left", padx=3)
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


    def log_line(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")


    def on_close(self):
        if self.eq_window is not None:
            self.eq_window.close()
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
