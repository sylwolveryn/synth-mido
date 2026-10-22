"""Hangesemények (Observer minta).

Minden megszólaló / elhallgató hang egy `NoteEvent`-ként megy át a `NoteBus`-on,
forrással együtt. A nézetek (zongora kiemelés, hangvizualizáció, hangszínszabályzó
ablak) feliratkoznak, így a hangforrásoknak nem kell tudniuk róluk.
"""

from typing import Callable, Dict, List, NamedTuple, Optional

# hangforrások
USER = "user"          # egér / számítógép billentyűzet
MIDI_IN = "midi_in"    # MIDI bemenet (a zongora)
PLAYBACK = "playback"  # felvétel visszajátszás


def controller(number: int) -> str:
    """A játékvezérlő forrás neve a hangszer fül sorszámával (2 = a 2. hangszer, az első vezérlő)."""
    return f"controller{number}"


class NoteEvent(NamedTuple):
    note: int
    on: bool
    velocity: int = 100
    source: str = USER


Listener = Callable[[NoteEvent], None]


class KeySources:
    """Melyik forrás tart éppen egy billentyűt (verem: a legutóbbi forrás színe látszik).

    Több forrás is lenyomhatja ugyanazt a hangot (pl. lejátszás és a játékos); a billentyű addig
    világít, amíg bármelyik tartja, mindig a legutóbb lenyomó színével."""

    def __init__(self):
        self._stack: Dict[int, List[str]] = {}

    def press(self, note: int, source: str) -> str:
        self._stack.setdefault(note, []).append(source)
        return source

    def release(self, note: int, source: str) -> Optional[str]:
        """Elengedés; a még tartó legutóbbi forrás, vagy None, ha senki nem tartja."""
        stack = self._stack.get(note)
        if not stack:
            return None
        if source in stack:
            stack.reverse()
            stack.remove(source)    # a legutóbbi ilyen forrás
            stack.reverse()
        else:
            stack.pop()             # ismeretlen forrás (pl. vészleállítás): a legutóbbi enged el
        if not stack:
            del self._stack[note]
            return None
        return stack[-1]

    def top(self, note: int) -> Optional[str]:
        stack = self._stack.get(note)
        return stack[-1] if stack else None

    def clear(self) -> None:
        self._stack.clear()


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
