"""Tesztek a kitartó pedálhoz: nyilvántartás, Szóköz kezelése, CC 64.

Futtatás:  python -m unittest test_sustain -v
"""

import contextlib
import io
import unittest
from unittest import mock

import keyboard_play as kp
import midi_controller
from sustain import SustainPedal
from test_audio_output import FakeTone
from test_playback import FakeTimer


class SustainPedalTests(unittest.TestCase):
    def setUp(self):
        self.stopped = []
        self.pedal = SustainPedal(self.stopped.append)

    def test_without_pedal_note_stops_on_key_up(self):
        self.assertTrue(self.pedal.key_up(60))
        self.assertEqual(self.pedal.sustained, set())

    def test_with_pedal_note_keeps_sounding_until_pedal_up(self):
        self.pedal.press()
        self.assertFalse(self.pedal.key_up(60))
        self.assertFalse(self.pedal.key_up(64))
        self.assertEqual(self.stopped, [])
        self.pedal.release()
        self.assertEqual(self.stopped, [60, 64])
        self.assertFalse(self.pedal.down)
        self.assertEqual(self.pedal.sustained, set())

    def test_key_still_held_when_pedal_released_keeps_sounding(self):
        self.pedal.press()
        self.pedal.key_down(67)          # le van nyomva, nem engedték el
        self.pedal.release()
        self.assertEqual(self.stopped, [])

    def test_retriggered_sustained_note_is_held_by_key_again(self):
        self.pedal.press()
        self.pedal.key_up(60)
        self.pedal.key_down(60)          # újra lenyomva pedál alatt
        self.pedal.release()
        self.assertEqual(self.stopped, [])
        self.assertTrue(self.pedal.key_up(60))

    def test_pedal_pressed_after_key_up_does_not_catch_it(self):
        self.assertTrue(self.pedal.key_up(60))
        self.pedal.press()
        self.pedal.release()
        self.assertEqual(self.stopped, [])


class SpaceKeyTests(unittest.TestCase):
    def setUp(self):
        self.timer = FakeTimer()
        self.pedal_log = []
        self.kb = kp.KeyboardPlayer(self.timer.after, self.timer.cancel, lambda n, on: None,
                                    on_pedal=self.pedal_log.append)

    def test_space_presses_and_releases_pedal(self):
        self.assertTrue(self.kb.press("space"))
        self.assertTrue(self.kb.pedal_held)
        self.assertTrue(self.kb.release("space"))
        self.timer.advance(0.05)
        self.assertEqual(self.pedal_log, [True, False])

    def test_space_auto_repeat_on_both_platforms(self):
        self.kb.press("space")
        for _ in range(3):
            self.kb.press("space")                          # Windows
        for _ in range(3):
            self.kb.release("space")
            self.kb.press("space")                          # X11
        self.timer.advance(0.1)
        self.assertEqual(self.pedal_log, [True])

    def test_release_all_lifts_pedal(self):
        self.kb.press("space")
        self.kb.release_all()
        self.assertEqual(self.pedal_log, [True, False])
        self.kb.release_all()
        self.assertEqual(self.pedal_log, [True, False])


class ControllerSustainTests(unittest.TestCase):
    def test_cc64_sent_to_active_output(self):
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(midi_controller.mido, "get_output_names", return_value=[]), \
                mock.patch.object(midi_controller.mido, "get_input_names", return_value=[]):
            c = midi_controller.VevorMIDIController(tone_factory=FakeTone)
            c.sustain(True)
            c.sustain(False)
        sent = [(m.type, m.control, m.value) for m in c.active_output.sent]
        self.assertEqual(sent, [("control_change", 64, 127), ("control_change", 64, 0)])

    def test_pedal_up_does_not_open_fallback(self):
        factory = mock.Mock(side_effect=FakeTone)
        with contextlib.redirect_stdout(io.StringIO()), \
                mock.patch.object(midi_controller.mido, "get_output_names", return_value=[]), \
                mock.patch.object(midi_controller.mido, "get_input_names", return_value=[]):
            c = midi_controller.VevorMIDIController(tone_factory=factory)
            c.sustain(False)
        factory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
