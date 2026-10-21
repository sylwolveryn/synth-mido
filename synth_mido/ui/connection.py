"""MIDI eszközök: listázás, csatlakozás, hangkimenet, hangszer, bemenet figyelése."""

from tkinter import messagebox

from synth_mido import config
from synth_mido.audio.tone_synth import ToneSynth
from synth_mido.core import events
from synth_mido.core.i18n import t
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
        self.log_line(t("log.devices", inputs=len(inputs), outputs=len(outputs)))


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
            self.connect_btn.configure(text=t("btn.connect"))
            self.log_line(t("log.disconnected"))
            self._activate_output("status.disconnected")
            return

        inp = self.input_var.get().strip() or None
        out = self.output_var.get().strip() or None
        if not inp and not out:
            messagebox.showwarning(t("msg.no_device.title"), t("msg.no_device"))
            return

        ok = self.controller.connect(input_name=inp, output_name=out)
        if not ok:
            messagebox.showerror(t("msg.error"), t("msg.connect_failed"))
            self._activate_output("status.connect_failed")
            return

        self.connect_btn.configure(text=t("btn.disconnect"))
        self.log_line(t("log.connected", input=inp or "-", output=out or "-"))
        self._activate_output()


    def _activate_output(self, idle_key: str = "status.idle"):
        """Az aktív hangkimenet kiírása az állapotsorba és a hangszer beállítása rajta."""
        self.idle_status_key = idle_key
        self._refresh_base_status()
        self.status_var.set(self.base_status)
        c = self.controller
        if c.fallback_error and not self.fallback_error_logged:
            self.fallback_error_logged = True
            self.log_line(t("audio.no_fallback", error=c.fallback_error_detail or c.fallback_error))
        self.on_instrument_change()


    def _refresh_base_status(self):
        """Az alap állapotsor szövege (kapcsolat + hangkimenet) az aktuális nyelven."""
        c = self.controller
        head = t("status.connected", device=c.device_name) if c.connected else t(self.idle_status_key)
        name = c.output_name
        if name == ToneSynth.name:
            name = t("audio.builtin")
        if name is None:
            self.base_status = t("status.no_output", head=head)
        elif c.using_fallback:
            self.base_status = t("status.fallback", head=head, name=name)
        else:
            self.base_status = head


    def require_output(self) -> bool:
        if self.controller.active_output is not None:
            return True
        messagebox.showinfo(t("msg.no_output.title"), t("msg.no_output"))
        return False


    def on_instrument_change(self, _event=None):
        label = self.instrument_var.get()
        self.draw_instrument_art()
        for name, num in config.INSTRUMENTS.items():
            if pretty_instrument(name) == label:
                self.recorder.set_instrument(name, num)  # felvétel közben a további hangok ezzel rögzülnek
                if self.controller.active_output is None:
                    return
                self.controller.change_instrument(num)
                self.log_line(t("log.instrument", name=label))
                return


    def toggle_listen(self):
        if self.listening:
            self.stop_listen()
            return
        if not self.controller.connected or not self.controller.input_port:
            messagebox.showinfo(t("msg.no_input.title"), t("msg.no_input"))
            return
        self.listening = True
        self.listen_btn.configure(text=t("btn.listen_stop"))
        self.log_line(t("log.listen_started"))
        self.poll_midi()


    def stop_listen(self):
        self.listening = False
        if self.listen_job:
            self.root.after_cancel(self.listen_job)
            self.listen_job = None
        self.listen_btn.configure(text=t("btn.listen_start"))


    def poll_midi(self):
        if not self.listening or not self.controller.input_port:
            return
        try:
            for msg in self.controller.input_port.iter_pending():
                if msg.type in ("note_on", "note_off"):
                    on = msg.type == "note_on" and msg.velocity > 0
                    action = "ON " if on else "OFF"
                    self.log_line(t("log.midi_note", action=action, note=note_label(msg.note), number=msg.note,
                                    velocity=msg.velocity))
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
            self.log_line(t("log.read_error", error=e))
            self.stop_listen()
            return
        self.listen_job = self.root.after(15, self.poll_midi)
