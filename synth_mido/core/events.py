"""Hangesemények (Observer minta).

Minden megszólaló / elhallgató hang egy `NoteEvent`-ként megy át a `NoteBus`-on,
forrással együtt. A nézetek (zongora kiemelés, hangvizualizáció, hangszínszabályzó
ablak) feliratkoznak, így a hangforrásoknak nem kell tudniuk róluk.
"""

from typing import Callable, List, NamedTuple

# hangforrások
USER = "user"          # egér / számítógép billentyűzet
MIDI_IN = "midi_in"    # MIDI bemenet (a zongora)
PLAYBACK = "playback"  # felvétel visszajátszás


class NoteEvent(NamedTuple):
    note: int
    on: bool
    velocity: int = 100
    source: str = USER


Listener = Callable[[NoteEvent], None]


class NoteBus:
    def __init__(self):
        self._listeners: List[Listener] = []

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        """Feliratkozás; a visszaadott függvény leiratkoztat."""
        self._listeners.append(listener)

        def unsubscribe():
            if listener in self._listeners:
                self._listeners.remove(listener)

        return unsubscribe

    def publish(self, note: int, on: bool, velocity: int = 100, source: str = USER) -> NoteEvent:
        event = NoteEvent(note, on, velocity, source)
        for listener in list(self._listeners):
            listener(event)
        return event

    @property
    def listener_count(self) -> int:
        return len(self._listeners)
