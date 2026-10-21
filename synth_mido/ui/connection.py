"""MIDI eszközök: listázás, csatlakozás, hangkimenet, hangszer, bemenet figyelése."""

from tkinter import messagebox

from synth_mido import config
from synth_mido.core import events
from synth_mido.core.piano_layout import note_label
from synth_mido.ui.common import (
    pretty_instrument,
)


class ConnectionMixin:

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
        label = self.instrument_var.get()
        for name, num in config.INSTRUMENTS.items():
            if pretty_instrument(name) == label:
                self.recorder.set_instrument(name, num)  # felvétel közben a további hangok ezzel rögzülnek
                if self.controller.active_output is None:
                    return
                self.controller.change_instrument(num)
                self.log_line(f"Hangszer: {label}")
                return


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
                    self.highlight(msg.note, on, msg.velocity, events.MIDI_IN)
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
