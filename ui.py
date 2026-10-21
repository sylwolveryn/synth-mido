import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

import config
import recorder
import theme
from midi_controller import VevorMIDIController

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
C_MAJOR_SCALE = [60, 62, 64, 65, 67, 69, 71, 72]
C_MAJOR_CHORD = [60, 64, 67]
DEMO_MELODY = [
    76, 75, 76, 75, 76, 71, 74, 72, 69, 60, 64, 69, 71, 64, 68, 71, 72, 64,
    76, 75, 76, 75, 76, 71, 74, 72, 69,
]


def note_label(note: int) -> str:
    return f"{NOTE_NAMES[note % 12]}{note // 12 - 1}"


def pretty_instrument(name: str) -> str:
    return name.replace("_", " ").title()


def format_seconds(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


THEME_LABELS = {
    theme.SYSTEM_MODE: "Rendszer",
    theme.LIGHT_MODE: "Világos",
    theme.DARK_MODE: "Sötét",
}
THEME_POLL_MS = 2000
RECORD_TICK_MS = 250


class PianoApp:
    WHITE_OFFSETS = [0, 2, 4, 5, 7, 9, 11]
    BLACK_OFFSETS = [1, 3, 6, 8, 10]
    START_NOTE = 48  # C3
    OCTAVES = 2

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VEVOR MIDI vezérlő")
        self.root.minsize(780, 620)
        self.root.geometry("860x700")

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

        self.theme_mode = theme.load_mode()
        self.scheme = theme.resolve_scheme(self.theme_mode)
        self.palette = theme.palette_for(self.scheme)
        self.theme_job = None
        self.style = ttk.Style(self.root)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.instrument_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Nincs csatlakozás")
        self.velocity_var = tk.IntVar(value=100)
        self.theme_var = tk.StringVar(value=THEME_LABELS[self.theme_mode])
        self.record_var = tk.StringVar(value="")

        self._build()
        self.apply_theme()
        self._schedule_theme_poll()
        self.refresh_devices()
        self._activate_output()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build(self):
        pad = {"padx": 10, "pady": 6}

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
        ttk.Scale(play, from_=1, to=127, variable=self.velocity_var, orient="horizontal", length=160).grid(
            row=0, column=3, sticky="ew", padx=4, pady=6
        )

        actions = ttk.Frame(play)
        actions.grid(row=1, column=0, columnspan=4, sticky="w", padx=8, pady=(0, 8))
        ttk.Button(actions, text="C-dúr skála", command=self.play_scale).pack(side="left", padx=3)
        ttk.Button(actions, text="C-dúr akkord", command=self.play_chord).pack(side="left", padx=3)
        ttk.Button(actions, text="Bemutató", command=self.play_demo).pack(side="left", padx=3)
        ttk.Button(actions, text="Leállítás", command=self.stop_playback).pack(side="left", padx=3)
        ttk.Button(actions, text="Minden hang ki", command=self.panic).pack(side="left", padx=3)

        play.columnconfigure(3, weight=1)

        piano_frame = ttk.LabelFrame(self.root, text="Zongora (kattints a billentyűkre)")
        piano_frame.pack(fill="x", **pad)
        self.canvas = tk.Canvas(piano_frame, height=150, bg=self.palette["piano_bg"], highlightthickness=0)
        self.canvas.pack(fill="x", padx=8, pady=8)
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

        self.log = tk.Text(listen, height=10, wrap="word", state="disabled")
        scroll = ttk.Scrollbar(listen, command=self.log.yview)
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=(0, 8))
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=(0, 8))

        ttk.Label(self.root, textvariable=self.status_var, style="Status.TLabel").pack(fill="x", padx=12, pady=(0, 10))

    # --- téma -------------------------------------------------------------

    def apply_theme(self):
        """Az aktív paletta alkalmazása az összes (már létező) widgetre."""
        p = self.palette
        font = (theme.FONT_FAMILY, theme.FONT_SIZE)
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont"):
            try:
                tkfont.nametofont(name).configure(family=theme.FONT_FAMILY, size=theme.FONT_SIZE)
            except tk.TclError:
                pass

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
        style.configure("Status.TLabel", background=p["bg"], foreground=p["muted"])
        style.configure("TLabelframe", background=p["bg"], bordercolor=p["border"], relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=p["bg"], foreground=p["muted"], font=(theme.FONT_FAMILY, theme.FONT_SIZE, "bold"))

        style.configure("TButton", background=p["surface"], foreground=p["fg"], bordercolor=p["border"], padding=(12, 5))
        style.map(
            "TButton",
            background=[("pressed", p["select_bg"]), ("active", p["select_bg"]), ("disabled", p["bg"])],
            foreground=[("disabled", p["muted"])],
        )
        style.configure("Accent.TButton", background=p["accent"], foreground=p["accent_fg"], bordercolor=p["accent"], padding=(12, 5))
        style.map(
            "Accent.TButton",
            background=[("pressed", p["accent"]), ("active", p["accent"]), ("disabled", p["bg"])],
            foreground=[("disabled", p["muted"])],
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
        style.configure("Horizontal.TScale", background=p["bg"], troughcolor=p["border"], bordercolor=p["border"])
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
        self.draw_piano()

    def _restyle_combobox_popdowns(self):
        """A már létrehozott legördülő listák színezése (az option_add csak az újakra hat)."""
        p = self.palette
        for combo in (self.input_combo, self.output_combo, self.instrument_combo, self.theme_combo):
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
            self.status_var.set(f"{head} — nincs hangkimenet")
        elif c.using_fallback:
            self.status_var.set(f"{head} — hang: {name} (alapértelmezett)")
        else:
            self.status_var.set(head)
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
        if not self.require_output() or self.playing:
            return
        self.playing = True
        vel = int(self.velocity_var.get())
        for note in C_MAJOR_CHORD:
            self.controller.note_on(note, vel)
            self.highlight(note, True)
        self.log_line("C-dúr akkord")
        self.play_job = self.root.after(1600, lambda: self._end_chord(C_MAJOR_CHORD))

    def _end_chord(self, notes):
        for note in notes:
            self.controller.note_off(note)
            self.highlight(note, False)
        self.playing = False
        self.play_job = None

    def _play_sequence(self, notes, hold_ms, gap_ms, label):
        if not self.require_output() or self.playing:
            return
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
        self.highlight(note, True)
        self.play_job = self.root.after(hold_ms, lambda: self._release_then_next(notes, index, hold_ms, gap_ms))

    def _release_then_next(self, notes, index, hold_ms, gap_ms):
        note = notes[index]
        self.controller.note_off(note)
        self.highlight(note, False)
        if not self.playing:
            return
        self.play_job = self.root.after(gap_ms, lambda: self._play_index(notes, index + 1, hold_ms, gap_ms))

    def stop_playback(self):
        self.playing = False
        if self.play_job:
            self.root.after_cancel(self.play_job)
            self.play_job = None
        self.panic()

    def panic(self):
        self.controller.panic()
        for note in list(self.active_notes):
            self.highlight(note, False)
        self.active_notes.clear()
        self.log_line("Minden hang leállítva")

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
                    self.highlight(msg.note, on)
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
        height = 150
        white_count = 7 * self.OCTAVES + 1
        white_w = width / white_count
        whites = []
        for octave in range(self.OCTAVES):
            base = self.START_NOTE + octave * 12
            for off in self.WHITE_OFFSETS:
                whites.append(base + off)
        whites.append(self.START_NOTE + self.OCTAVES * 12)

        for i, note in enumerate(whites):
            x0 = i * white_w
            x1 = x0 + white_w
            color = p["key_white_active"] if note in self.active_notes else p["key_white"]
            kid = self.canvas.create_rectangle(x0, 0, x1, height, fill=color, outline=p["key_outline"], width=1, tags=("key", f"n{note}"))
            self.canvas.create_text(x0 + white_w / 2, height - 16, text=note_label(note), fill=p["key_label"], font=(theme.FONT_FAMILY, 8))
            self.key_ids[note] = kid

        black_w = white_w * 0.6
        black_h = height * 0.62
        for octave in range(self.OCTAVES):
            base = self.START_NOTE + octave * 12
            for off in self.BLACK_OFFSETS:
                note = base + off
                whites_before = sum(1 for n in whites if n < note)
                cx = whites_before * white_w
                x0 = cx - black_w / 2
                x1 = cx + black_w / 2
                color = p["key_black_active"] if note in self.active_notes else p["key_black"]
                kid = self.canvas.create_rectangle(x0, 0, x1, black_h, fill=color, outline=p["key_outline"], tags=("key", f"n{note}"))
                self.key_ids[note] = kid

    def note_from_event(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in reversed(items):
            for tag in self.canvas.gettags(item):
                if tag.startswith("n") and tag[1:].isdigit():
                    return int(tag[1:])
        return None

    def on_piano_press(self, event):
        note = self.note_from_event(event)
        if note is None:
            return
        audible = self.controller.active_output is not None
        if not audible and not self.recorder.is_recording:
            return
        if note in self.held_notes:
            return
        velocity = int(self.velocity_var.get())
        if audible:
            self.controller.note_on(note, velocity)
        self.recorder.note_on(note, velocity)
        self.held_notes.add(note)
        self.highlight(note, True)
        self.log_line(f"ON  {note_label(note)} ({note})")

    def on_piano_release(self, _event=None):
        if not self.held_notes:
            return
        for note in list(self.held_notes):
            self.controller.note_off(note)
            self.recorder.note_off(note)
            self.highlight(note, False)
        self.held_notes.clear()

    def highlight(self, note: int, on: bool):
        if on:
            self.active_notes.add(note)
        else:
            self.active_notes.discard(note)
        kid = self.key_ids.get(note)
        if not kid:
            return
        is_black = (note % 12) in self.BLACK_OFFSETS
        p = self.palette
        if on:
            self.canvas.itemconfigure(kid, fill=p["key_black_active"] if is_black else p["key_white_active"])
        else:
            self.canvas.itemconfigure(kid, fill=p["key_black"] if is_black else p["key_white"])

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
        ttk.Button(btns, text="Összes kijelölése", command=self.select_all_records).pack(side="left", padx=(0, 3))
        ttk.Button(btns, text="Törlés", command=self.delete_selected_records).pack(side="left", padx=3)
        ttk.Button(btns, text="Frissítés", command=self.refresh_records).pack(side="left", padx=3)
        ttk.Button(btns, text="Mappa megnyitása", command=self.open_records_folder).pack(side="left", padx=3)
        ttk.Button(btns, text="Bezárás", command=win.destroy).pack(side="right")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

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
        self._finish_recording()
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
