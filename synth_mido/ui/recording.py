"""Felvétel: indítás / leállítás és mentés párbeszéd."""

import tkinter as tk
from tkinter import messagebox, ttk

from synth_mido import config
from synth_mido.core import recorder
from synth_mido.ui.common import (
    RECORD_TICK_MS,
    format_seconds,
    pretty_instrument,
)


class RecordingMixin:

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
        # lejátszás közben indított felvétel: a már szóló visszajátszott hangok is bekerülnek
        for note, velocity, instrument in self.player.sounding_voices():
            self.recorder.note_on(note, velocity, instrument)
        self.record_btn.configure(text="■ Leállítás", style="Accent.TButton")
        if self.controller.connected and self.controller.input_port:
            if not self.listening:
                self.toggle_listen()
            self.log_line(f"Felvétel indítva ({pretty_instrument(name)})")
        else:
            self.log_line("Felvétel indítva kapcsolat nélkül — a képernyős zongora hangjai rögzülnek")
        if self.player.is_playing:
            self.log_line(f"A lejátszott „{self.player.record_name}” is bekerül a felvételbe")
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
            f"{', '.join(pretty_instrument(i['name']) for i in recorder.instruments_of(record))}"
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
