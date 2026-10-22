"""Nyelvváltás: a feliratok kulcsokhoz kötve, váltáskor mind újratöltődik (TASK-021)."""

from synth_mido.core import doubling, i18n
from synth_mido.core.i18n import t
from synth_mido.fx import effects
from synth_mido.skins import registry, theme


class LanguageMixin:

    def bind_text(self, widget, text, option="text"):
        """A widget szövegét a `text()` függvény adja, nyelvváltáskor újra.

        `option`: "text" (felirat), "title" (ablakcím), ("heading", oszlop) (táblázat fejléc),
        vagy None, ha a függvény maga állítja be a widgetet. Visszaadja a widgetet."""
        binding = (widget, option, text)
        self.lang_bindings.append(binding)
        self._apply_binding(binding)
        return widget


    def tr(self, widget, key, option="text"):
        """Rövidítés: a widget felirata egy fordítási kulcs."""
        return self.bind_text(widget, lambda: t(key), option)


    @staticmethod
    def _apply_binding(binding):
        widget, option, text = binding
        if option is None:
            text()
        elif option == "title":
            widget.title(text())
        elif isinstance(option, tuple) and option[0] == "heading":
            widget.heading(option[1], text=text())
        else:
            widget.configure(**{option: text()})


    def on_language_change(self, _event=None):
        index = self.language_combo.current()
        code = i18n.LANGUAGES[index] if 0 <= index < len(i18n.LANGUAGES) else i18n.REFERENCE
        self.set_language(code)


    def set_language(self, code: str, save: bool = True):
        """Nyelv váltása: az egész nyelv újratöltődik, és minden nyitott ablak minden felirata frissül."""
        self.language = i18n.set_language(code)
        if save:
            theme.save_setting("language", self.language)
        self.apply_language()
        self.log_line(t("log.language", name=i18n.language_name(self.language)))


    def apply_language(self):
        alive = []
        for binding in self.lang_bindings:
            try:
                exists = binding[0].winfo_exists()
            except Exception:
                exists = False
            if exists:
                self._apply_binding(binding)
                alive.append(binding)
        self.lang_bindings = alive  # a bezárt ablakok kötései kikerülnek
        self.root.title(t("app.title"))
        # a nyelvfüggő listák: értékek és a kiválasztott elem
        self.language_var.set(i18n.language_name(self.language))
        self.skin_combo.configure(values=[s.label for s in registry.all_skins()])
        self.skin_var.set(self.skin.label)
        self.variant_combo.configure(values=[registry.variant_label(v) for v in registry.VARIANTS_ORDER])
        self.variant_var.set(registry.variant_label(self.variant))
        self.effect_combo.configure(values=[effects.label(e) for e in effects.ids()])
        self.effect_var.set(effects.label(self.effect_id))
        self.doubling_combo.configure(values=[doubling.label(m) for m in doubling.MODES])
        self.doubling_var.set(doubling.label(self.doubler.mode))
        self.octave_label_var.set(t("piano.octaves", octaves=self.octaves.label()))
        # szakaszcímek, fejléc felirat, illusztráció felirata
        self.apply_theme()
        # állapotsor és lejátszó sáv
        self._refresh_base_status()
        self._player_changed()
        self.refresh_records()
