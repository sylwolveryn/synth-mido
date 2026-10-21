"""Tesztek a tartalék hangkimenethez: hanggenerátor és kimenetválasztás.

Nem kell hozzájuk valódi MIDI eszköz vagy hangkártya (a mido és az eszközök mockolva).
Futtatás:  python -m unittest test_audio_output -v
"""

import contextlib
import io
import unittest
from unittest import mock

import mido
import numpy as np

from synth_mido.audio import midi_controller, tone_synth
from synth_mido.audio.tone_synth import ToneSynth, ToneSynthUnavailable
from tests.fakes import FakePort, FakeTone

SR = 8000


def msg(kind, **kw):
    return mido.Message(kind, **kw)


class ToneSynthTests(unittest.TestCase):
    def setUp(self):
        self.synth = ToneSynth(samplerate=SR, start_stream=False)

    def test_silent_without_notes(self):
        out = self.synth.render(256)
        self.assertEqual(out.dtype, np.float32)
        self.assertEqual(len(out), 256)
        self.assertFalse(np.any(out))

    def test_note_on_makes_sound_in_range(self):
        self.synth.send(msg("note_on", note=69, velocity=127))
        self.synth.send(msg("note_on", note=72, velocity=127))
        out = self.synth.render(SR // 10)
        self.assertGreater(np.max(np.abs(out)), 0.05)
        self.assertLessEqual(np.max(np.abs(out)), 1.0)
        self.assertEqual(self.synth.active_notes, [69, 72])

    def test_louder_velocity_is_louder(self):
        quiet = ToneSynth(samplerate=SR, start_stream=False)
        quiet.send(msg("note_on", note=60, velocity=20))
        self.synth.send(msg("note_on", note=60, velocity=120))
        self.assertGreater(np.max(np.abs(self.synth.render(800))), np.max(np.abs(quiet.render(800))))

    def test_note_off_fades_out_and_removes_voice(self):
        self.synth.send(msg("note_on", note=60, velocity=100))
        self.synth.render(400)
        self.synth.send(msg("note_off", note=60))
        self.synth.render(int(SR * tone_synth.RELEASE) + 10)
        self.assertEqual(self.synth.active_notes, [])
        self.assertFalse(np.any(self.synth.render(100)))

    def test_note_on_zero_velocity_is_note_off(self):
        self.synth.send(msg("note_on", note=60, velocity=100))
        self.synth.send(msg("note_on", note=60, velocity=0))
        self.synth.render(int(SR * tone_synth.RELEASE) + 10)
        self.assertEqual(self.synth.active_notes, [])

    def test_held_note_decays_by_itself(self):
        self.synth.send(msg("note_on", note=60, velocity=100))
        for _ in range(10):
            self.synth.render(SR)
        self.assertEqual(self.synth.active_notes, [])

    def test_all_notes_off_and_close(self):
        for note in (60, 64, 67):
            self.synth.send(msg("note_on", note=note, velocity=100))
        self.synth.send(msg("control_change", control=123, value=0))
        self.assertEqual(self.synth.active_notes, [])
        self.synth.send(msg("note_on", note=60, velocity=100))
        self.synth.close()
        self.assertEqual(self.synth.active_notes, [])

    def test_program_change_is_ignored(self):
        self.synth.send(msg("program_change", program=40))
        self.assertFalse(np.any(self.synth.render(64)))

    def test_missing_sounddevice_raises_clear_error(self):
        with mock.patch.dict("sys.modules", {"sounddevice": None}):
            with self.assertRaises(ToneSynthUnavailable):
                ToneSynth()

    def test_frequency(self):
        self.assertAlmostEqual(tone_synth.note_frequency(69), 440.0)
        self.assertAlmostEqual(tone_synth.note_frequency(81), 880.0)






class OutputSelectionTests(unittest.TestCase):
    def make(self, outputs, tone_factory=FakeTone):
        self.opened = {}

        def open_output(name):
            if name not in outputs:
                raise OSError(f"no port {name}")
            port = FakePort(name)
            self.opened.setdefault(name, []).append(port)
            return port

        for target, value in (
            ("get_output_names", mock.Mock(return_value=list(outputs))),
            ("get_input_names", mock.Mock(return_value=[])),
            ("open_output", mock.Mock(side_effect=open_output)),
        ):
            patcher = mock.patch.object(midi_controller.mido, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        out = io.StringIO()
        self.addCleanup(out.close)
        stack = contextlib.ExitStack()
        stack.enter_context(contextlib.redirect_stdout(out))
        self.addCleanup(stack.close)
        return midi_controller.VevorMIDIController(tone_factory=tone_factory)

    def notes_sent(self, port):
        return [(m.type, m.note) for m in port.sent if m.type in ("note_on", "note_off")]

    def test_prefers_os_synth_port(self):
        c = self.make(["VEVOR MIDI 1", "Microsoft GS Wavetable Synth 0"])
        c.note_on(60, 90)
        port = self.opened["Microsoft GS Wavetable Synth 0"][0]
        self.assertIs(c.active_output, port)
        self.assertTrue(c.using_fallback)
        self.assertEqual(c.output_name, "Microsoft GS Wavetable Synth 0")
        self.assertEqual(self.notes_sent(port), [("note_on", 60)])

    def test_instrument_change_reaches_os_synth(self):
        c = self.make(["Microsoft GS Wavetable Synth 0"])
        c.change_instrument(40)
        port = self.opened["Microsoft GS Wavetable Synth 0"][0]
        self.assertEqual([(m.type, m.program) for m in port.sent], [("program_change", 40)])

    def test_tone_synth_when_no_os_synth(self):
        c = self.make(["Some Other Port"])
        c.note_on(64, 100)
        c.note_off(64)
        self.assertIsInstance(c.active_output, FakeTone)
        self.assertEqual(c.output_name, ToneSynth.name)
        self.assertEqual(self.notes_sent(c.active_output), [("note_on", 64), ("note_off", 64)])

    def test_no_output_at_all_does_not_crash_and_reports_once(self):
        factory = mock.Mock(side_effect=ToneSynthUnavailable("nincs hangeszköz"))
        c = self.make([], tone_factory=factory)
        c.note_on(60)
        c.note_off(60)
        c.change_instrument(3)
        c.panic()
        self.assertIsNone(c.active_output)
        self.assertIsNone(c.output_name)
        self.assertIn("nincs hangeszköz", c.fallback_error)
        self.assertEqual(factory.call_count, 1)

    def test_connected_output_wins_and_disconnect_returns_to_fallback(self):
        c = self.make(["VEVOR OUT", "Microsoft GS Wavetable Synth 0"])
        c.note_on(60)
        fallback = self.opened["Microsoft GS Wavetable Synth 0"][0]

        self.assertTrue(c.connect(output_name="VEVOR OUT"))
        self.assertTrue(fallback.closed)
        c.note_on(62)
        device = self.opened["VEVOR OUT"][0]
        self.assertIs(c.active_output, device)
        self.assertFalse(c.using_fallback)
        self.assertEqual(self.notes_sent(device), [("note_on", 62)])

        c.close()
        c.note_on(64)
        reopened = self.opened["Microsoft GS Wavetable Synth 0"][1]
        self.assertIs(c.active_output, reopened)
        self.assertEqual(self.notes_sent(reopened), [("note_on", 64)])

    def test_connecting_to_the_os_synth_itself(self):
        c = self.make(["Microsoft GS Wavetable Synth 0"])
        c.note_on(60)
        self.assertTrue(c.connect(output_name="Microsoft GS Wavetable Synth 0"))
        first, second = self.opened["Microsoft GS Wavetable Synth 0"]
        self.assertTrue(first.closed)
        self.assertIs(c.active_output, second)
        self.assertFalse(c.using_fallback)

    def test_input_only_connection_uses_fallback(self):
        c = self.make(["Microsoft GS Wavetable Synth 0"])
        with mock.patch.object(midi_controller.mido, "open_input", return_value=FakePort("VEVOR IN")):
            self.assertTrue(c.connect(input_name="VEVOR IN"))
        self.assertTrue(c.using_fallback)

    def test_panic_silences_fallback_without_opening_it(self):
        factory = mock.Mock(side_effect=FakeTone)
        c = self.make([], tone_factory=factory)
        c.panic()
        factory.assert_not_called()
        c.note_on(60)
        c.panic()
        tone = c.active_output
        self.assertIn(("control_change", 123), [(m.type, getattr(m, "control", None)) for m in tone.sent])
        self.assertEqual(sum(1 for m in tone.sent if m.type == "note_off"), 128)

    def test_shutdown_closes_fallback(self):
        c = self.make([])
        c.note_on(60)
        tone = c.active_output
        c.shutdown()
        self.assertTrue(tone.closed)
        self.assertIsNone(c.fallback)


if __name__ == "__main__":
    unittest.main()
