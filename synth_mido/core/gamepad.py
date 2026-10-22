"""Játékvezérlők (gamepad, joystick) mint további hangszerek — Tk-tól független.

* **Backend** — a csatlakoztatott vezérlők listája és állapota. Windowson a beépített
  winmm joystick API (ctypes, nincs új függőség; USB és Bluetooth vezérlő egyaránt),
  máshol üres backend. Tesztben hamis backend.
* **PadMapper** — egy vezérlő állapotváltozásaiból zenei műveletek: a 12 gomb a dúr
  skála fokai a kiinduló hangtól, a D-pad fel / le oktávot, balra / jobbra hangnemet
  vált, a bal kar függőlegesen a hangerő, a ravasz (Z tengely) a kitartó pedál.
* **ControllerSlots** — a csatlakoztatott vezérlők stabil sorszáma (2., 3. … hangszer),
  saját MIDI csatornával; ki- és bedugáskor (hot-plug) frissül.
"""

import ctypes
import sys
from typing import Dict, List, NamedTuple, Optional, Tuple

from synth_mido.core.piano_layout import FIRST_NOTE, LAST_NOTE

MAX_CONTROLLERS = 4
CONTROLLER_CHANNELS = (15, 14, 13, 12)   # MIDI csatorna slotonként (a 0. a billentyűzeté, 1–11 a felvételeké)
SCALE = (0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19)   # 12 gomb: dúr skála fokai másfél oktávon
DEFAULT_BASE = 60          # C4
NEUTRAL_VELOCITY = 100
AXIS_DEADZONE = 0.2
TRIGGER_THRESHOLD = 0.5


class DeviceInfo(NamedTuple):
    id: int        # a backend saját azonosítója (winmm: joystick szám)
    name: str
    buttons: int


class PadState(NamedTuple):
    buttons: int = 0                      # bitmaszk: az 1. gomb a 0. bit
    axes: Tuple[float, ...] = (0.0,) * 6  # X, Y, Z, R, U, V — -1..1, 0 a közép (Y: -1 = fel)
    pov: Optional[int] = None             # D-pad: 0 fel, 90 jobbra, 180 le, 270 balra; None = nincs lenyomva


class NullBackend:
    """Nincs elérhető joystick API (nem Windows): nincs vezérlő."""

    def devices(self) -> List[DeviceInfo]:
        return []

    def poll(self, device_id: int) -> Optional[PadState]:
        return None


class _JOYINFOEX(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint32) for n in (
        "dwSize", "dwFlags", "dwXpos", "dwYpos", "dwZpos", "dwRpos", "dwUpos", "dwVpos", "dwButtons",
        "dwButtonNumber", "dwPOV", "dwReserved1", "dwReserved2")]


class _JOYCAPSW(ctypes.Structure):
    _fields_ = [
        ("wMid", ctypes.c_uint16), ("wPid", ctypes.c_uint16), ("szPname", ctypes.c_wchar * 32),
        *[(n, ctypes.c_uint32) for n in ("wXmin", "wXmax", "wYmin", "wYmax", "wZmin", "wZmax", "wNumButtons",
                                         "wPeriodMin", "wPeriodMax", "wRmin", "wRmax", "wUmin", "wUmax", "wVmin",
                                         "wVmax", "wCaps", "wMaxAxes", "wNumAxes", "wMaxButtons")],
        ("szRegKey", ctypes.c_wchar * 32), ("szOEMVxD", ctypes.c_wchar * 260),
    ]


JOY_RETURNALL = 0xFF
JOY_POVCENTERED = 0xFFFF


class WinMMBackend:
    """Windows multimédia joystick API: minden HID játékvezérlő (Xbox, PlayStation, általános), USB és Bluetooth."""

    def __init__(self):
        self._winmm = ctypes.windll.winmm
        self._caps: Dict[int, _JOYCAPSW] = {}

    def devices(self) -> List[DeviceInfo]:
        w = self._winmm
        try:
            w.joyConfigChanged(0)   # nélküle az indulás után bedugott vezérlőt nem látja
        except Exception:
            pass
        found = []
        info = _JOYINFOEX(dwSize=ctypes.sizeof(_JOYINFOEX), dwFlags=JOY_RETURNALL)
        for joy_id in range(min(w.joyGetNumDevs(), 16)):
            if w.joyGetPosEx(joy_id, ctypes.byref(info)) != 0:
                self._caps.pop(joy_id, None)
                continue
            caps = _JOYCAPSW()
            if w.joyGetDevCapsW(joy_id, ctypes.byref(caps), ctypes.sizeof(caps)) != 0:
                continue
            self._caps[joy_id] = caps
            found.append(DeviceInfo(joy_id, caps.szPname or f"Joystick {joy_id + 1}", caps.wNumButtons))
        return found

    def poll(self, device_id: int) -> Optional[PadState]:
        caps = self._caps.get(device_id)
        info = _JOYINFOEX(dwSize=ctypes.sizeof(_JOYINFOEX), dwFlags=JOY_RETURNALL)
        if caps is None or self._winmm.joyGetPosEx(device_id, ctypes.byref(info)) != 0:
            return None

        def norm(value, lo, hi):
            return 0.0 if hi <= lo else max(-1.0, min(1.0, 2 * (value - lo) / (hi - lo) - 1))

        axes = (norm(info.dwXpos, caps.wXmin, caps.wXmax), norm(info.dwYpos, caps.wYmin, caps.wYmax),
                norm(info.dwZpos, caps.wZmin, caps.wZmax), norm(info.dwRpos, caps.wRmin, caps.wRmax),
                norm(info.dwUpos, caps.wUmin, caps.wUmax), norm(info.dwVpos, caps.wVmin, caps.wVmax))
        pov = None if info.dwPOV == JOY_POVCENTERED else info.dwPOV // 100
        return PadState(info.dwButtons, axes, pov)


def default_backend():
    if sys.platform.startswith("win"):
        try:
            return WinMMBackend()
        except (AttributeError, OSError):
            pass
    return NullBackend()


# --- egy vezérlő: állapot → zenei műveletek --------------------------------------------------

ON, OFF, SUSTAIN, SHIFT = "on", "off", "sustain", "shift"


class Action(NamedTuple):
    kind: str          # on | off | sustain | shift
    note: int = 0
    velocity: int = 0
    down: bool = False  # sustain


def _pov_direction(pov: Optional[int]) -> Optional[str]:
    if pov is None:
        return None
    return {0: "up", 90: "right", 180: "down", 270: "left"}.get(int(round(pov / 90.0)) * 90 % 360)


class PadMapper:
    """Egy vezérlő leképezése. A lenyomáskor indított hangot jegyzi meg, így a hangnemváltás
    lenyomott gomb mellett sem hagy lógó hangot."""

    def __init__(self, base: int = DEFAULT_BASE):
        self.base = base           # az 1. gomb hangja (oktáv)
        self.transpose = 0         # félhang, -11..11
        self._prev = PadState()
        self._held: Dict[int, int] = {}   # gomb index -> megszólaltatott hang
        self.sustain = False

    def note_for(self, button: int) -> Optional[int]:
        if not 0 <= button < len(SCALE):
            return None
        note = self.base + self.transpose + SCALE[button]
        return note if FIRST_NOTE <= note <= LAST_NOTE else None

    @staticmethod
    def velocity(state: PadState) -> int:
        y = state.axes[1] if len(state.axes) > 1 else 0.0
        if abs(y) < AXIS_DEADZONE:
            return NEUTRAL_VELOCITY
        if y < 0:   # kar fel: hangosabb
            return int(NEUTRAL_VELOCITY + (127 - NEUTRAL_VELOCITY) * min(1.0, -y))
        return int(NEUTRAL_VELOCITY - (NEUTRAL_VELOCITY - 30) * min(1.0, y))

    def range_label(self) -> Tuple[int, int]:
        """A gombokkal elérhető legalsó és legfelső hang."""
        return self.base + self.transpose, self.base + self.transpose + SCALE[-1]

    def update(self, state: PadState) -> List[Action]:
        actions: List[Action] = []
        prev = self._prev
        # D-pad: csak az új irány számít (lenyomás pillanata)
        direction, was = _pov_direction(state.pov), _pov_direction(prev.pov)
        if direction and direction != was:
            if direction == "up" and self.base + 12 + SCALE[0] <= LAST_NOTE:
                self.base += 12
            elif direction == "down" and self.base - 12 >= FIRST_NOTE:
                self.base -= 12
            elif direction == "right":
                self.transpose = min(self.transpose + 1, 11)
            elif direction == "left":
                self.transpose = max(self.transpose - 1, -11)
            actions.append(Action(SHIFT))
        # ravasz / Z tengely: kitartó pedál
        z = state.axes[2] if len(state.axes) > 2 else 0.0
        sustain = abs(z) >= TRIGGER_THRESHOLD
        if sustain != self.sustain:
            self.sustain = sustain
            actions.append(Action(SUSTAIN, down=sustain))
        # gombok
        changed = state.buttons ^ prev.buttons
        for button in range(len(SCALE)):
            bit = 1 << button
            if not changed & bit:
                continue
            if state.buttons & bit:
                note = self.note_for(button)
                if note is not None:
                    self._held[button] = note
                    actions.append(Action(ON, note, self.velocity(state)))
            elif button in self._held:
                actions.append(Action(OFF, self._held.pop(button)))
        self._prev = state
        return actions

    def release_all(self) -> List[Action]:
        """Leválasztáskor: minden lenyomott hang és a pedál felengedése."""
        actions = [Action(OFF, note) for note in self._held.values()]
        self._held.clear()
        if self.sustain:
            self.sustain = False
            actions.append(Action(SUSTAIN, down=False))
        self._prev = PadState()
        return actions


# --- több vezérlő: stabil sorszám és hot-plug -----------------------------------------------

class Slot:
    """Egy hangszer fül egy vezérlőhöz (2., 3. … hangszer)."""

    def __init__(self, index: int):
        self.index = index                       # 0 → „2. hangszer”
        self.channel = CONTROLLER_CHANNELS[index]
        self.device: Optional[DeviceInfo] = None
        self.mapper = PadMapper()

    @property
    def connected(self) -> bool:
        return self.device is not None

    @property
    def number(self) -> int:
        """A fül sorszáma a felületen (1 = billentyűzet, így a vezérlők 2-től)."""
        return self.index + 2


class ControllerSlots:
    """A vezérlők slotokhoz rendelése: egy már látott vezérlő megtartja a helyét; az új az első szabad
    helyre kerül. A 2. hangszer slotja mindig létezik (vezérlő nélkül is)."""

    def __init__(self, backend=None):
        self.backend = backend or default_backend()
        self.slots = [Slot(i) for i in range(MAX_CONTROLLERS)]

    def connected(self) -> List[Slot]:
        return [s for s in self.slots if s.connected]

    def visible(self) -> List[Slot]:
        """A felületen látható fülek: a 2. mindig, a többi csak csatlakoztatott vezérlővel."""
        return [s for s in self.slots if s.index == 0 or s.connected]

    def rescan(self) -> Tuple[List[Slot], List[Slot]]:
        """Csatlakozott és levált slotok (ebben a sorrendben)."""
        devices = {d.id: d for d in self.backend.devices()}
        removed = []
        for slot in self.slots:
            if slot.connected and slot.device.id not in devices:
                removed.append(slot)
                slot.device = None
        taken = {s.device.id for s in self.slots if s.connected}
        added = []
        for dev_id, dev in sorted(devices.items()):
            if dev_id in taken:
                continue
            free = next((s for s in self.slots if not s.connected), None)
            if free is None:
                break
            free.device = dev
            free.mapper = PadMapper()
            added.append(free)
        return added, removed

    def poll(self, slot: Slot) -> Optional[PadState]:
        return self.backend.poll(slot.device.id) if slot.connected else None
