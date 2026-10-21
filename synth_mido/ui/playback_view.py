"""Lejátszás: skála / akkord / bemutató, felvétel visszajátszás és a lejátszó sáv."""

from pathlib import Path
from tkinter import filedialog, messagebox

from synth_mido import config
from synth_mido.core import events, playback, recorder
from synth_mido.ui.common import (
    C_MAJOR_CHORD,
    C_MAJOR_SCALE,
    DEMO_MELODY,
    PLAYER_TICK_MS,
    SEEK_MARGIN,
    format_seconds,
    pretty_instrument,
)


class PlaybackMixin:

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
            self.highlight(note, True, vel, events.DEMO)
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
        self.highlight(note, True, vel, events.DEMO)
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
        self.highlight(note, on, velocity, events.PLAYBACK)


    def _on_player_finish(self):
        self.log_line(f"Lejátszás vége: {self.player.record_name}")
        self._player_changed()


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
