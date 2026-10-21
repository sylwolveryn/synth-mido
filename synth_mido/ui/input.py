"""Játszott hangok útja: billentyűzet, pedál, oktáv duplázás."""

import tkinter as tk

from synth_mido.core import doubling, events
from synth_mido.skins import theme


class InputMixin:

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
            self.highlight(n, True, velocity, events.USER)
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


    TEXT_INPUT_CLASSES = ("Entry", "TEntry", "TCombobox", "Spinbox", "TSpinbox")


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
        # módosító billentyűket (Ctrl / Alt / Num Lock) nem nézünk: a hangbillentyű mindig szól
        if self._is_text_input(event.widget):
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
