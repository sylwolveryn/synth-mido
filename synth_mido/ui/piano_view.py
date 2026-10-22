"""A 88 billentyűs zongora rajza, egér kezelés és kiemelés."""


from synth_mido.core import events, piano_layout
from synth_mido.core.i18n import t
from synth_mido.core.piano_layout import note_label
from synth_mido.skins import key_colors, theme
from synth_mido.ui.common import (
    PIANO_HEIGHT,
)


class PianoViewMixin:

    def draw_piano(self):
        p = self.palette
        self.canvas.delete("all")
        self.key_ids.clear()
        width = max(self.canvas.winfo_width(), 100)
        h = self.canvas.winfo_height()
        height = h if h > 1 else PIANO_HEIGHT   # kis ablakban a billentyűk alacsonyabbak (nem levágva)
        k = height / PIANO_HEIGHT   # a jelölők helye a magassággal arányos
        labels = set(piano_layout.label_notes())
        for key in piano_layout.layout(width, height):
            color = self._key_fill(key.note, key.black)
            kid = self.canvas.create_rectangle(
                key.x0, key.y0, key.x1, key.y1, fill=color, outline=p["key_outline"], width=1,
                tags=("key", f"n{key.note}"),
            )
            self.key_ids[key.note] = kid
            if key.note in labels:
                cx = (key.x0 + key.x1) / 2
                middle = key.note == piano_layout.MIDDLE_C
                self.canvas.create_text(
                    cx, height - 12, text=note_label(key.note), fill=p["accent"] if middle else p["key_label"],
                    font=(self.font_family, 7, "bold" if middle else "normal"), state="disabled",
                )
                if middle:
                    self.canvas.create_oval(cx - 3, height - 30 * k, cx + 3, height - 30 * k + 6, fill=p["accent"], outline="",
                                            state="disabled")
        self._draw_keyboard_range(width, height)


    def _draw_keyboard_range(self, width, height):
        """A számítógép-billentyűzettel elérhető tartomány: sáv felül + betűk (ha be van kapcsolva)."""
        k = height / PIANO_HEIGHT
        p = self.palette
        low, high = self.keyboard.range_notes()
        keys = {k.note: k for k in piano_layout.layout(width, height)}
        x0 = min(keys[n].x0 for n in range(low, high + 1))
        x1 = max(keys[n].x1 for n in range(low, high + 1))
        # naplemente színátmenet a tartomány sávon (a világos / sötét témában ez az akcentus árnyalatai)
        segments = 24
        for i in range(segments):
            t = i / (segments - 1)
            color = theme.mix(p["sun_top"], p["sun_mid"], t * 2) if t < 0.5 else theme.mix(p["sun_mid"], p["sun_bottom"], t * 2 - 1)
            sx0 = x0 + (x1 - x0) * i / segments
            sx1 = x0 + (x1 - x0) * (i + 1) / segments + 1
            self.canvas.create_rectangle(sx0, 0, sx1, 4, fill=color, outline="", state="disabled", tags=("range",))
        # a többi kiválasztott oktáv: vékonyabb jelölő ugyanakkora tartományon
        for offset in self.octaves.offsets():
            notes = [n for n in range(low + offset, high + offset + 1) if n in keys]
            if notes:
                self.canvas.create_rectangle(min(keys[n].x0 for n in notes), 0, max(keys[n].x1 for n in notes), 3,
                                             fill=p["accent2"], outline="", state="disabled", tags=("range-extra",))
        if not self.show_letters_var.get():
            return
        for note, letter in self.keyboard.key_labels().items():
            key = keys[note]
            cx = (key.x0 + key.x1) / 2
            if key.black:
                y, color = key.y1 - 9, p["key_white"]
            else:
                y, color = height - 44 * k, p["accent"]
            self.canvas.create_text(cx, y, text=letter, fill=color, font=(self.font_family, 7, "bold"),
                                    state="disabled", tags=("letter",))


    def shift_octave(self, octaves: int):
        if not self.keyboard.shift(octaves):
            self.log_line(t("log.kb_edge"))


    def _on_keyboard_range(self):
        low, high = self.keyboard.range_notes()
        self.kb_range_var.set(f"{note_label(low)}–{note_label(high)}")
        self.octaves.set_base(self.keyboard.base)  # a billentyűzet oktávja követi az X / C váltást
        self._sync_octaves()

    # --- többoktávos játék (TASK-017) ---------------------------------------

    def toggle_octave(self, base: int):
        """Oktáv be / ki az Oktávok listában; a billentyűzet oktávja mindig marad."""
        self.octaves.toggle(base)
        self._sync_octaves()
        self.root.focus_set()

    def _sync_octaves(self):
        self.doubler.set_extra_offsets(self.octaves.offsets())
        for base, var in self.octave_vars.items():
            var.set(self.octaves.is_selected(base))
        self.octave_label_var.set(t("piano.octaves", octaves=self.octaves.label()))
        self.draw_piano()


    def note_from_event(self, event):
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in reversed(items):
            for tag in self.canvas.gettags(item):
                if tag.startswith("n") and tag[1:].isdigit():
                    return int(tag[1:])
        return None


    def on_piano_press(self, event):
        note = self.note_from_event(event)
        if note is None or note in self.held_notes:
            return
        if self._user_note_on(note):
            self.held_notes.add(note)
            self.log_line(f"ON  {note_label(note)} ({note})")


    def on_piano_release(self, _event=None):
        if not self.held_notes:
            return
        for note in list(self.held_notes):
            self._user_note_off(note)
        self.held_notes.clear()


    def highlight(self, note: int, on: bool, velocity: int = 100, source: str = events.USER):
        """Egy hang megszólalt / elhallgatott: közzététel a NoteBus-on. A zongora kiemelés, a hangvizualizáció
        és a hangszínszabályzó ablak feliratkozóként kapja meg (Observer)."""
        self.notes.publish(note, on, velocity, source)

    def _paint_key(self, event: events.NoteEvent):
        """NoteBus feliratkozó: a billentyű színe és az aktív hangok halmaza."""
        note, on = event.note, event.on
        if on:
            self.key_sources.press(note, event.source)
            self.active_notes.add(note)
        elif self.key_sources.release(note, event.source) is None:
            self.active_notes.discard(note)
        kid = self.key_ids.get(note)
        if kid:
            self.canvas.itemconfigure(kid, fill=self._key_fill(note, piano_layout.is_black(note)))

    def _key_fill(self, note: int, black: bool) -> str:
        """A billentyű színe: alapszín, vagy a legutóbb lenyomó forrás színe (billentyűzet, lejátszás, vezérlők)."""
        source = self.key_sources.top(note)
        if source is None:
            return self.palette["key_black" if black else "key_white"]
        if self._key_colors_for is not self.palette:  # skinváltáskor újraszámoljuk
            self._key_colors_for = self.palette
            self._key_colors = key_colors.source_colors(self.palette)
        return key_colors.color_for(self._key_colors, source, black)
