"""Felvétel: indítás / leállítás és mentés párbeszéd."""

import tkinter as tk
from tkinter import messagebox, ttk

from synth_mido import config
from synth_mido.core import recorder
from synth_mido.core.i18n import t
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
        self.record_btn.configure(text=t("btn.record_stop"), style="Accent.TButton")
        if self.controller.connected and self.controller.input_port:
            if not self.listening:
                self.toggle_listen()
            self.log_line(t("log.rec_started", instrument=pretty_instrument(name)))
        else:
            self.log_line(t("log.rec_started_blind"))
        if self.player.is_playing:
            self.log_line(t("log.rec_with_playback", name=self.player.record_name))
        self._tick_recording()


    def _tick_recording(self):
        self.record_job = None
        if not self.recorder.is_recording:
            return
        self.record_var.set(t("rec.counter", time=format_seconds(self.recorder.elapsed()), count=self.recorder.note_count))
        self.record_job = self.root.after(RECORD_TICK_MS, self._tick_recording)


    def _finish_recording(self):
        """Felvétel leállítása, majd mentés / elvetés párbeszéd (üres felvételnél nincs)."""
        if not self.recorder.is_recording:
            return
        record = self.recorder.stop()
        if self.record_job:
            self.root.after_cancel(self.record_job)
            self.record_job = None
        self.record_btn.configure(text=t("btn.record"), style="TButton")
        self.record_var.set("")
        if not record["notes"]:
            self.log_line(t("log.rec_empty"))
            return
        self._ask_save(record)


    def _ask_save(self, record: dict):
        """Modális ablak: név megadása (alapértelmezett: felvetel_YYYYMMDD_HHMMSS), Mentés vagy Elvetés."""
        dlg = tk.Toplevel(self.root)
        self.save_dialog = dlg
        dlg.title(t("save.title"))
        dlg.configure(bg=self.palette["bg"])
        dlg.resizable(False, False)
        dlg.transient(self.root)

        body = ttk.Frame(dlg, padding=14)
        body.pack(fill="both", expand=True)
        summary = t("save.summary", count=len(record["notes"]), duration=format_seconds(record["duration"]),
                    instruments=", ".join(pretty_instrument(i["name"]) for i in recorder.instruments_of(record)))
        ttk.Label(body, text=summary, style="Status.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Label(body, text=t("save.name")).grid(row=1, column=0, sticky="w", padx=(0, 8))
        name_var = tk.StringVar(value=recorder.default_name())
        entry = ttk.Entry(body, textvariable=name_var, width=38)
        entry.grid(row=1, column=1, sticky="ew")
        ttk.Label(body, text=t("save.location", path=recorder.RECORDS_DIR), style="Status.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(6, 10)
        )

        def save(_event=None):
            try:
                try:
                    path = recorder.save_record(record, name_var.get())
                except FileExistsError as e:
                    if not messagebox.askyesno(t("msg.exists.title"), t("msg.exists", name=e.args[0].name), parent=dlg):
                        return
                    path = recorder.save_record(record, name_var.get(), overwrite=True)
            except ValueError as e:
                messagebox.showerror(t("msg.bad_name.title"), str(e), parent=dlg)
                return
            except OSError as e:
                messagebox.showerror(t("msg.save_error.title"), t("msg.save_error", error=e), parent=dlg)
                return
            self.log_line(t("log.saved", path=path))
            self.status_var.set(t("status.saved", name=path.name))
            dlg.destroy()
            self.refresh_records()

        def discard(_event=None):
            if messagebox.askyesno(t("msg.discard.title"), t("msg.discard"), parent=dlg):
                self.log_line(t("log.discarded"))
                dlg.destroy()

        btns = ttk.Frame(body)
        btns.grid(row=3, column=0, columnspan=2, sticky="e")
        ttk.Button(btns, text=t("btn.discard"), command=discard).pack(side="left", padx=3)
        ttk.Button(btns, text=t("btn.save"), command=save, style="Accent.TButton").pack(side="left", padx=3)
        body.columnconfigure(1, weight=1)

        dlg.protocol("WM_DELETE_WINDOW", discard)
        dlg.bind("<Return>", save)
        dlg.bind("<Escape>", discard)
        entry.focus_set()
        entry.select_range(0, "end")
        dlg.grab_set()
        self.root.wait_window(dlg)
        self.save_dialog = None
