"""Lejátszás: felvétel visszajátszás és a lejátszó sáv."""

from pathlib import Path
from tkinter import filedialog, messagebox

from synth_mido import config
from synth_mido.core import events, playback, recorder
from synth_mido.core.i18n import t
from synth_mido.ui.common import (
    PLAYER_TICK_MS,
    SEEK_MARGIN,
    format_seconds,
    pretty_instrument,
)


class PlaybackMixin:

    def stop_playback(self, quiet: bool = False):
        """Leállítás: a felvétel lejátszása, a pedál és minden szóló hang."""
        self.panic(quiet)


    def panic(self, quiet: bool = False):
        was_active = self.player.is_playing or self.player.is_paused
        self.player.stop()
        self.set_pedal(False)
        self.controller.panic()
        self.key_sources.clear()   # vészleállítás: minden forrás elenged
        for note in list(self.active_notes):
            self.highlight(note, False)
        self.active_notes.clear()
        if was_active:
            self.status_var.set(self.base_status)
        self._refresh_player_ui()
        if quiet:
            return
        if was_active:
            self.log_line(t("log.playback_stopped", name=self.player.record_name))
        self.log_line(t("log.all_stopped"))


    def open_record_file(self):
        folder = recorder.RECORDS_DIR if recorder.RECORDS_DIR.is_dir() else recorder.RECORDS_DIR.parent
        path = filedialog.askopenfilename(
            parent=self.root,
            title=t("open.title"),
            initialdir=str(folder),
            filetypes=[(t("open.records"), "*.json"), (t("open.all_files"), "*.*")],
        )
        if path:
            self.play_record_file(path)


    def play_record_file(self, path, parent=None):
        """Felvétel betöltése és lejátszása; a hangszere lesz az alapértelmezett (átállítható)."""
        path = Path(path)
        try:
            record = recorder.load_record(path)
        except ValueError as e:
            messagebox.showerror(t("msg.bad_record.title"), f"{path.name}\n\n{e}", parent=parent or self.root)
            return
        if not self.require_output():
            return
        self.stop_playback(quiet=True)
        if record["version"] == recorder.V1:
            # egy hangszer a fő csatornán: a felvétel hangszere lesz kiválasztva, de átállítható
            self.record_channels = {}
            instrument = playback.default_instrument(record, config.INSTRUMENTS)
            self.instrument_var.set(pretty_instrument(instrument))
            self.on_instrument_change()
        else:
            # minden hangszer saját csatornán; a felhasználó hangszere (0. csatorna) nem változik
            self.record_channels = playback.assign_channels(recorder.instruments_of(record))
            for program, channel in self.record_channels.items():
                self.controller.set_program(channel, program)
        if not record["notes"]:
            messagebox.showinfo(t("msg.empty_record.title"), t("msg.empty_record", name=path.stem),
                                parent=parent or self.root)
            return
        self.player.set_speed(float(self.speed_var.get().rstrip("x")))
        self.player.play(record, path.stem)
        names = ", ".join(pretty_instrument(i["name"]) for i in recorder.instruments_of(record))
        self.log_line(t("log.playing", name=path.stem, count=len(record["notes"]),
                        duration=format_seconds(self.player.duration), instruments=names))
        self._player_changed()


    def _on_player_note(self, note: int, velocity: int, on: bool, instrument=None):
        """A lejátszó hangja: a saját csatornáján szól, és bekerül egy éppen futó felvételbe is."""
        channel = self.record_channels.get(instrument["program"]) if instrument else None
        if on:
            self.controller.note_on(note, velocity, channel)
            self.recorder.note_on(note, velocity, instrument)
        else:
            self.controller.note_off(note, channel)
            self.recorder.note_off(note, instrument)
        self.highlight(note, on, velocity, events.PLAYBACK)


    def _on_player_finish(self):
        self.log_line(t("log.playback_end", name=self.player.record_name))
        self._player_changed()


    def player_play_pause(self):
        if not self.player.is_loaded:
            return
        if not self.player.is_playing:
            if not self.require_output():
                return
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
            self.status_var.set(t("status.playing", name=name, speed=self.speed_var.get()))
        elif self.player.is_paused:
            self.status_var.set(t("status.paused", name=name))
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
        self.player_name_var.set(p.record_name or t("player.none"))
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
