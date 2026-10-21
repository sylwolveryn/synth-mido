import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

import config
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


THEME_LABELS = {
    theme.SYSTEM_MODE: "Rendszer",
    theme.LIGHT_MODE: "Világos",
    theme.DARK_MODE: "Sötét",
}
THEME_POLL_MS = 2000


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

        self._build()
        self.apply_theme()
        self._schedule_theme_poll()
        self.refresh_devices()
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
        self.listen_btn = ttk.Button(listen, text="Figyelés indítása", command=self.toggle_listen)
        self.listen_btn.pack(anchor="w", padx=8, pady=6)

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
            self.stop_playback()
            self.stop_listen()
            self.controller.close()
            self.connect_btn.configure(text="Csatlakozás")
            self.status_var.set("Kapcsolat bontva")
            self.log_line("Kapcsolat bontva")
            return

        inp = self.input_var.get().strip() or None
        out = self.output_var.get().strip() or None
        if not inp and not out:
            messagebox.showwarning("Nincs eszköz", "Válassz MIDI bemenetet vagy kimenetet.")
            return

        ok = self.controller.connect(input_name=inp, output_name=out)
        if not ok:
            messagebox.showerror("Hiba", "Nem sikerült csatlakozni a MIDI eszközhöz.")
            self.status_var.set("Csatlakozás sikertelen")
            return

        self.connect_btn.configure(text="Leválasztás")
        self.status_var.set(f"Csatlakozva: {self.controller.device_name}")
        self.log_line(f"Csatlakozva — be: {inp or '-'} / ki: {out or '-'}")
        self.on_instrument_change()

    def require_output(self) -> bool:
        if self.controller.connected and self.controller.output_port:
            return True
        messagebox.showinfo("Nincs kapcsolat", "Előbb csatlakozz egy MIDI kimenethez.")
        return False

    def on_instrument_change(self, _event=None):
        if not self.controller.connected or not self.controller.output_port:
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
        if self.controller.connected:
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
        if not self.controller.connected or not self.controller.output_port:
            return
        if note in self.held_notes:
            return
        self.controller.note_on(note, int(self.velocity_var.get()))
        self.held_notes.add(note)
        self.highlight(note, True)
        self.log_line(f"ON  {note_label(note)} ({note})")

    def on_piano_release(self, _event=None):
        if not self.held_notes:
            return
        for note in list(self.held_notes):
            self.controller.note_off(note)
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

    def on_close(self):
        if self.theme_job:
            self.root.after_cancel(self.theme_job)
            self.theme_job = None
        self.stop_playback()
        self.stop_listen()
        if self.controller.connected:
            self.controller.close()
        self.root.destroy()


def run():
    root = tk.Tk()
    PianoApp(root)
    root.mainloop()


if __name__ == "__main__":
    run()
