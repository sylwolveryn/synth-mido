"""Tesztek a játékvezérlőkhöz (hamis backenddel), a billentyű forrásokhoz és a forrásonkénti színekhez.

Futtatás:  python -m unittest tests.test_gamepad -v
"""

import unittest

from synth_mido.core import events, gamepad, playback
from synth_mido.core.gamepad import OFF, ON, SHIFT, SUSTAIN, PadMapper, PadState
from synth_mido.skins import catalog, key_colors, registry  # noqa: F401 — a catalog regisztrálja a skineket
from tests.fakes_pad import FakePadBackend


def press(*buttons, axes=(0.0,) * 6, pov=None):
    mask = 0
    for b in buttons:
        mask |= 1 << b
    return PadState(mask, tuple(axes), pov)


class MapperTests(unittest.TestCase):
    def setUp(self):
        self.m = PadMapper()

    def test_buttons_play_the_major_scale_from_c4(self):
        notes = [self.m.update(press(b))[0].note for b in range(12) for _ in [self.m.update(PadState())]]
        self.assertEqual(notes, [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79])

    def test_press_and_release_pairs(self):
        self.assertEqual(self.m.update(press(0, 2)), [(ON, 60, 100, False), (ON, 64, 100, False)])
        self.assertEqual(self.m.update(press(2)), [(OFF, 60, 0, False)])
        self.assertEqual(self.m.update(PadState()), [(OFF, 64, 0, False)])
        self.assertEqual(self.m.update(PadState()), [])

    def test_dpad_changes_octave_and_key_once_per_press(self):
        self.assertEqual(self.m.update(press(pov=0))[0].kind, SHIFT)
        self.assertEqual(self.m.update(press(pov=0)), [])          # nyomva tartva nem ismétel
        self.m.update(PadState())
        self.m.update(press(pov=90))
        self.m.update(PadState())
        self.assertEqual(self.m.update(press(0))[0].note, 73)    # C5 + 1 félhang
        self.m.update(PadState())
        self.m.update(press(pov=180))
        self.m.update(PadState())
        self.m.update(press(pov=270))
        self.m.update(PadState())
        self.assertEqual(self.m.range_label(), (60, 79))

    def test_octave_stays_on_the_keyboard(self):
        for _ in range(10):
            self.m.update(press(pov=180))
            self.m.update(PadState())
        self.assertGreaterEqual(self.m.base, 21)
        for _ in range(20):
            self.m.update(press(pov=0))
            self.m.update(PadState())
        self.assertLessEqual(self.m.base, 108)
        notes = [self.m.note_for(b) for b in range(12)]
        self.assertTrue(all(n is None or 21 <= n <= 108 for n in notes))

    def test_shift_while_held_releases_the_started_note(self):
        self.m.update(press(0))
        self.m.update(press(0, pov=0))
        self.assertEqual(self.m.update(PadState()), [(OFF, 60, 0, False)])

    def test_left_stick_sets_velocity(self):
        up = self.m.update(press(0, axes=(0, -1, 0, 0, 0, 0)))[0].velocity
        self.m.update(PadState())
        down = self.m.update(press(0, axes=(0, 1, 0, 0, 0, 0)))[0].velocity
        self.m.update(PadState())
        mid = self.m.update(press(0, axes=(0, 0.1, 0, 0, 0, 0)))[0].velocity
        self.assertEqual((up, mid), (127, 100))
        self.assertLess(down, 50)

    def test_trigger_is_the_sustain_pedal(self):
        self.assertEqual(self.m.update(press(axes=(0, 0, 0.9, 0, 0, 0))), [(SUSTAIN, 0, 0, True)])
        self.assertEqual(self.m.update(press(axes=(0, 0, -0.8, 0, 0, 0))), [])
        self.assertEqual(self.m.update(PadState()), [(SUSTAIN, 0, 0, False)])

    def test_release_all(self):
        self.m.update(press(0, 4, axes=(0, 0, 1, 0, 0, 0)))
        kinds = sorted((a.kind, a.note) for a in self.m.release_all())
        self.assertEqual(kinds, [(OFF, 60), (OFF, 67), (SUSTAIN, 0)])


class SlotTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakePadBackend()
        self.slots = gamepad.ControllerSlots(self.backend)

    def test_second_instrument_is_always_visible(self):
        self.assertEqual([s.number for s in self.slots.visible()], [2])
        self.assertFalse(self.slots.visible()[0].connected)
        self.assertEqual(self.slots.rescan(), ([], []))

    def test_hot_plug_adds_tabs_and_keeps_slots_stable(self):
        self.backend.plug(3, "Xbox")
        added, _ = self.slots.rescan()
        self.assertEqual([(s.number, s.device.name) for s in added], [(2, "Xbox")])
        self.backend.plug(0, "PS5")
        self.backend.plug(7, "Generic")
        added, _ = self.slots.rescan()
        self.assertEqual([s.number for s in added], [3, 4])
        self.assertEqual([s.number for s in self.slots.visible()], [2, 3, 4])
        self.backend.unplug(0)
        _, removed = self.slots.rescan()
        self.assertEqual([s.number for s in removed], [3])
        self.assertEqual([s.number for s in self.slots.visible()], [2, 4])   # a többiek helye nem változik
        self.backend.unplug(3)
        self.slots.rescan()
        self.assertEqual([s.number for s in self.slots.visible()], [2, 4])   # a 2. fül vezérlő nélkül is látszik

    def test_at_most_four_controllers(self):
        for i in range(6):
            self.backend.plug(i)
        added, _ = self.slots.rescan()
        self.assertEqual(len(added), gamepad.MAX_CONTROLLERS)

    def test_poll_and_unplug(self):
        self.backend.plug(1)
        slot = self.slots.rescan()[0][0]
        self.backend.set(1, buttons=1)
        self.assertEqual(self.slots.poll(slot).buttons, 1)
        self.backend.unplug(1)
        self.assertIsNone(self.slots.poll(slot))

    def test_controller_channels_are_reserved(self):
        channels = [s.channel for s in self.slots.slots]
        self.assertEqual(len(set(channels)), gamepad.MAX_CONTROLLERS)
        self.assertFalse(set(channels) & set(playback.RECORD_CHANNELS) | {0, playback.DRUM_CHANNEL} & set(channels))

    def test_null_backend(self):
        self.assertEqual(gamepad.NullBackend().devices(), [])
        self.assertIsNone(gamepad.NullBackend().poll(0))


class KeySourceTests(unittest.TestCase):
    def test_newest_source_wins_and_key_stays_lit_until_all_release(self):
        k = events.KeySources()
        k.press(60, events.PLAYBACK)
        k.press(60, events.controller(2))
        self.assertEqual(k.top(60), "controller2")
        self.assertEqual(k.release(60, events.controller(2)), events.PLAYBACK)
        self.assertIsNone(k.release(60, events.PLAYBACK))
        self.assertIsNone(k.top(60))

    def test_unknown_release_pops_the_newest(self):
        k = events.KeySources()
        k.press(60, events.USER)
        k.press(60, events.PLAYBACK)
        self.assertEqual(k.release(60, "valami"), events.USER)
        k.clear()
        self.assertIsNone(k.top(60))
        self.assertIsNone(k.release(61, events.USER))


class ColourTests(unittest.TestCase):
    SOURCES = [events.USER, events.PLAYBACK] + [events.controller(n) for n in range(2, 2 + gamepad.MAX_CONTROLLERS)]

    def test_every_source_has_a_distinct_visible_colour_in_every_skin(self):
        for skin in registry.all_skins():
            for scheme in ("dark", "light"):
                p = skin.palette(scheme)
                colors = key_colors.source_colors(p)
                self.assertEqual(colors[events.MIDI_IN], colors[events.USER])
                for black in (False, True):
                    values = [key_colors.color_for(colors, s, black) for s in self.SOURCES]
                    worst = min(key_colors.distance(a, b) for i, a in enumerate(values) for b in values[i + 1:])
                    self.assertGreaterEqual(worst, key_colors.MIN_DISTANCE, (skin.id, scheme, black, values))
                    base = p["key_black" if black else "key_white"]
                    for s, c in zip(self.SOURCES[1:], values[1:]):
                        self.assertGreaterEqual(key_colors.distance(c, base), key_colors.MIN_DISTANCE, (skin.id, s))

    def test_playback_differs_from_live_playing(self):
        for skin in registry.all_skins():
            colors = key_colors.source_colors(skin.palette("dark"))
            self.assertNotEqual(colors[events.PLAYBACK][0], colors[events.USER][0])
            self.assertNotEqual(colors[events.PLAYBACK][1], colors[events.USER][1])

    def test_unknown_source_uses_the_keyboard_colour(self):
        colors = key_colors.source_colors(registry.get("synthwave").dark)
        self.assertEqual(key_colors.color_for(colors, "nincs", False), colors[events.USER][0])


if __name__ == "__main__":
    unittest.main()
