"""Hamis játékvezérlő backend a tesztekhez: a vezérlők és állapotuk kézzel állítható."""

from synth_mido.core.gamepad import DeviceInfo, PadState


class FakePadBackend:
    def __init__(self):
        self.pads = {}     # id -> [DeviceInfo, PadState]

    def plug(self, dev_id, name="Fake Pad", buttons=12):
        self.pads[dev_id] = [DeviceInfo(dev_id, name, buttons), PadState()]

    def unplug(self, dev_id):
        self.pads.pop(dev_id, None)

    def set(self, dev_id, buttons=0, axes=(0.0,) * 6, pov=None):
        self.pads[dev_id][1] = PadState(buttons, tuple(axes), pov)

    def devices(self):
        return [info for info, _ in self.pads.values()]

    def poll(self, dev_id):
        pad = self.pads.get(dev_id)
        return pad[1] if pad else None
