"""Játékvezérlők mint további hangszerek: fülek a Lejátszás részben, hot-plug figyelés, hangok kezelése."""

import tkinter as tk
from tkinter import ttk

from synth_mido import config
from synth_mido.core import events, gamepad
from synth_mido.core.i18n import t
from synth_mido.core.piano_layout import note_label
from synth_mido.core.sustain import SustainPedal
from synth_mido.skins import key_colors
from synth_mido.ui.common import pretty_instrument

RESCAN_MS = 2000   # új / kihúzott vezérlő keresése
POLL_MS = 16       # a csatlakoztatott vezérlők állapota (~60 / mp)


class ControllerTab:
    """Egy vezérlő fülének widgetjei és hangszere."""

    def __init__(self, slot: gamepad.Slot, frame: ttk.Frame):
        self.slot, self.frame = slot, frame
        self.instrument_var = tk.StringVar(value=pretty_instrument(next(iter(config.INSTRUMENTS))))
        self.status_var = tk.StringVar()
        self.combo = None
        self.swatch = None
        self.pedal = None
        self.shown = False


class ControllerMixin:

    def _init_controllers(self, backend=None):
        self.pads = gamepad.ControllerSlots(backend)
        self.pad_tabs = {}
        self.pad_rescan_job = None
        self.pad_poll_job = None


    def _build_instrument_tabs(self, parent):
        """A hangszer rész füles: 1. billentyűzet / egér, 2. … játékvezérlők. Visszaadja a billentyűzet fül keretét."""
        nb = self.instrument_tabs = ttk.Notebook(parent)
        keyboard_tab = ttk.Frame(nb, padding=0)
        nb.add(keyboard_tab)
        self.bind_text(nb, lambda: nb.tab(keyboard_tab, text=t("ctrl.tab_keyboard")), option=None)
        for slot in self.pads.slots:
            frame = ttk.Frame(nb, padding=0)
            tab = self.pad_tabs[slot.index] = ControllerTab(slot, frame)
            tab.pedal = SustainPedal(lambda note, s=slot: self._pad_stop(s, note))
            tab.swatch = tk.Frame(frame, width=14, height=14, highlightthickness=1)
            tab.swatch.grid(row=0, column=0, padx=(8, 0), pady=4)
            self.tr(ttk.Label(frame), "play.instrument").grid(row=0, column=1, sticky="w", padx=8, pady=4)
            tab.combo = ttk.Combobox(frame, textvariable=tab.instrument_var, state="readonly", width=24,
                                     values=[pretty_instrument(n) for n in config.INSTRUMENTS])
            tab.combo.grid(row=0, column=2, sticky="w", padx=4, pady=4)
            tab.combo.bind("<<ComboboxSelected>>", lambda _e, s=slot: self._pad_instrument_changed(s))
            ttk.Label(frame, textvariable=tab.status_var, style="Status.TLabel").grid(
                row=0, column=3, sticky="w", padx=8, pady=4)
            frame.columnconfigure(3, weight=1)
        self._sync_controller_tabs()
        return keyboard_tab


    def _pad_instrument(self, slot):
        label = self.pad_tabs[slot.index].instrument_var.get()
        for name, program in config.INSTRUMENTS.items():
            if pretty_instrument(name) == label:
                return {"name": name, "program": program}
        return {"name": next(iter(config.INSTRUMENTS)), "program": 0}


    def _pad_instrument_changed(self, slot):
        if slot.connected:
            self.controller.set_program(slot.channel, self._pad_instrument(slot)["program"])
        self.root.focus_set()


    # --- fülek -----------------------------------------------------------------------------------

    def _sync_controller_tabs(self):
        """A fülek láthatósága, felirata és állapota: a 2. hangszer mindig látszik (vezérlő nélkül letiltva),
        a többi csak csatlakoztatott vezérlővel."""
        nb = self.instrument_tabs
        visible = {s.index for s in self.pads.visible()}
        for slot in self.pads.slots:
            tab = self.pad_tabs[slot.index]
            if slot.index in visible:
                if tab.shown:
                    nb.tab(tab.frame, state="normal")
                else:
                    nb.add(tab.frame)
                    tab.shown = True
                nb.tab(tab.frame, text=t("ctrl.tab", number=slot.number))
            elif tab.shown:
                if nb.select() == str(tab.frame):
                    nb.select(0)
                nb.hide(tab.frame)
                tab.shown = False
            tab.combo.state(["!disabled"] if slot.connected else ["disabled"])
            if slot.connected:
                low, high = slot.mapper.range_label()
                tab.status_var.set(t("ctrl.status", name=slot.device.name, low=note_label(low), high=note_label(high)))
            else:
                tab.status_var.set(t("ctrl.none"))
        self.refresh_swatches()


    def refresh_swatches(self):
        """A fülek és a lejátszó sáv színmintái: ugyanazok a színek, amikkel a billentyűk világítanak."""
        colors = key_colors.source_colors(self.palette)
        for slot in self.pads.slots:
            tab = self.pad_tabs.get(slot.index)
            if tab is not None:
                tab.swatch.configure(bg=colors[events.controller(slot.number)][0],
                                     highlightbackground=self.palette["border"])
        for name, source in (("keyboard_swatch", events.USER), ("playback_swatch", events.PLAYBACK)):
            if hasattr(self, name):
                getattr(self, name).configure(bg=colors[source][0], highlightbackground=self.palette["border"])


    # --- figyelés (hot-plug) és lekérdezés --------------------------------------------------------

    def start_controllers(self):
        self._pad_rescan()


    def _pad_rescan(self):
        self.pad_rescan_job = None
        try:
            added, removed = self.pads.rescan()
        except Exception as e:   # a joystick API hibája ne állítsa meg a programot
            added, removed = [], []
            self.log_line(t("ctrl.error", error=e))
        for slot in removed:
            self._pad_release(slot)
            self.log_line(t("log.ctrl_removed", number=slot.number))
        for slot in added:
            self.controller.set_program(slot.channel, self._pad_instrument(slot)["program"])
            self.log_line(t("log.ctrl_added", number=slot.number, name=slot.device.name))
            self.log_line(t("ctrl.hint"))
        if added or removed:
            self._sync_controller_tabs()
        if self.pads.connected() and self.pad_poll_job is None:
            self.pad_poll_job = self.root.after(POLL_MS, self._pad_poll)
        self.pad_rescan_job = self.root.after(RESCAN_MS, self._pad_rescan)


    def _pad_poll(self):
        self.pad_poll_job = None
        lost = False
        for slot in self.pads.connected():
            state = self.pads.poll(slot)
            if state is None:   # kihúzták: a következő keresés leválasztja
                lost = True
                continue
            shifted = False
            for action in slot.mapper.update(state):
                shifted |= self._pad_action(slot, action)
            if shifted:
                self._sync_controller_tabs()
        if lost and self.pad_rescan_job is not None:
            self.root.after_cancel(self.pad_rescan_job)
            self.pad_rescan_job = self.root.after(0, self._pad_rescan)
        if self.pads.connected():
            self.pad_poll_job = self.root.after(POLL_MS, self._pad_poll)


    def _pad_action(self, slot, action) -> bool:
        """Egy vezérlő művelet; True, ha a fül feliratát frissíteni kell (oktáv / hangnem váltás)."""
        tab = self.pad_tabs[slot.index]
        if action.kind == gamepad.ON:
            tab.pedal.key_down(action.note)
            self.controller.note_on(action.note, action.velocity, slot.channel)
            self.recorder.note_on(action.note, action.velocity, self._pad_instrument(slot))
            self.highlight(action.note, True, action.velocity, events.controller(slot.number))
        elif action.kind == gamepad.OFF:
            if tab.pedal.key_up(action.note):
                self._pad_stop(slot, action.note)
        elif action.kind == gamepad.SUSTAIN:
            if action.down:
                tab.pedal.press()
            else:
                tab.pedal.release()
        elif action.kind == gamepad.SHIFT:
            return True
        return False


    def _pad_stop(self, slot, note):
        self.controller.note_off(note, slot.channel)
        self.recorder.note_off(note, self._pad_instrument(slot))
        self.highlight(note, False, 0, events.controller(slot.number))


    def _pad_release(self, slot):
        """Leválasztás / kilépés: a vezérlő minden hangja és pedálja felenged."""
        for action in slot.mapper.release_all():
            self._pad_action(slot, action)
        self.pad_tabs[slot.index].pedal.release()


    def stop_controllers(self):
        for job in (self.pad_rescan_job, self.pad_poll_job):
            if job is not None:
                self.root.after_cancel(job)
        self.pad_rescan_job = self.pad_poll_job = None
        for slot in self.pads.connected():
            self._pad_release(slot)
