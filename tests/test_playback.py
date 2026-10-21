"""Tesztek a playback modulhoz: ütemezés, alapértelmezett hangszer, lejátszó.

Tk, MIDI és hangeszköz nélkül futnak (az óra és az időzítő hamisított).
Futtatás:  python -m unittest test_playback -v
"""

import unittest

from synth_mido.core import playback
from synth_mido.core.playback import Event, Player, build_schedule, default_instrument
from tests.fakes import FakeTimer

INSTRUMENTS = {"acoustic_grand_piano": 0, "electric_piano_1": 4, "violin": 40}


def record(*notes, instrument=("acoustic_grand_piano", 0)):
    return {
        "format": "synth-mido-record",
        "version": 1,
        "created": "2026-10-21T20:00:00",
        "instrument": {"name": instrument[0], "program": instrument[1]},
        "duration": max((s + d for _, _, s, d in notes), default=0.0),
        "notes": [{"note": n, "velocity": v, "start": s, "duration": d} for n, v, s, d in notes],
    }


def simple(events):
    return [(e.time, "on" if e.on else "off", e.note) for e in events]


class ScheduleTests(unittest.TestCase):
    def test_empty_record(self):
        self.assertEqual(build_schedule(record()), [])

    def test_single_note(self):
        self.assertEqual(build_schedule(record((60, 90, 0.5, 0.25))), [
            Event(0.5, True, 60, 90),
            Event(0.75, False, 60, 0),
        ])

    def test_sorted_by_time_even_if_file_is_not(self):
        rec = record((64, 80, 1.0, 0.5), (60, 100, 0.0, 0.5))
        self.assertEqual(simple(build_schedule(rec)), [
            (0.0, "on", 60), (0.5, "off", 60), (1.0, "on", 64), (1.5, "off", 64),
        ])

    def test_overlapping_different_notes(self):
        rec = record((60, 100, 0.0, 1.0), (64, 100, 0.25, 1.0), (67, 100, 0.5, 0.25))
        self.assertEqual(simple(build_schedule(rec)), [
            (0.0, "on", 60), (0.25, "on", 64), (0.5, "on", 67),
            (0.75, "off", 67), (1.0, "off", 60), (1.25, "off", 64),
        ])

    def test_repeated_note_back_to_back_releases_before_retrigger(self):
        rec = record((60, 100, 0.0, 0.5), (60, 70, 0.5, 0.5))
        self.assertEqual(simple(build_schedule(rec)), [
            (0.0, "on", 60), (0.5, "off", 60), (0.5, "on", 60), (1.0, "off", 60),
        ])

    def test_overlapping_repeat_of_same_note_is_cut(self):
        rec = record((60, 100, 0.0, 2.0), (60, 70, 0.5, 0.5))
        events = build_schedule(rec)
        self.assertEqual(simple(events), [
            (0.0, "on", 60), (0.5, "off", 60), (0.5, "on", 60), (1.0, "off", 60),
        ])
        self.assertEqual(events[2].velocity, 70)

    def test_same_note_same_start_keeps_one(self):
        rec = record((60, 100, 0.0, 1.0), (60, 50, 0.0, 0.5))
        self.assertEqual(len([e for e in build_schedule(rec) if e.on]), 1)

    def test_zero_length_note_still_ends_after_it_starts(self):
        events = build_schedule(record((60, 100, 0.3, 0.0)))
        self.assertEqual([e.on for e in events], [True, False])
        self.assertAlmostEqual(events[1].time, 0.3 + playback.MIN_NOTE)

    def test_every_note_on_has_a_matching_later_note_off(self):
        rec = record((60, 100, 0.0, 0.3), (60, 90, 0.1, 0.1), (62, 80, 0.1, 0.0), (60, 70, 0.1, 0.4), (64, 60, 0.2, 0.2))
        sounding = set()
        for e in build_schedule(rec):
            if e.on:
                self.assertNotIn(e.note, sounding)
                sounding.add(e.note)
            else:
                sounding.discard(e.note)
        self.assertEqual(sounding, set())


class DefaultInstrumentTests(unittest.TestCase):
    def test_by_name(self):
        self.assertEqual(default_instrument(record(instrument=("violin", 40)), INSTRUMENTS), "violin")

    def test_unknown_name_falls_back_to_program(self):
        self.assertEqual(default_instrument(record(instrument=("ep1", 4)), INSTRUMENTS), "electric_piano_1")

    def test_unknown_falls_back_to_first(self):
        self.assertEqual(default_instrument(record(instrument=("x", 99)), INSTRUMENTS), "acoustic_grand_piano")




class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.timer = FakeTimer()
        self.log = []
        self.finished = 0
        self.player = Player(
            after=self.timer.after,
            cancel=self.timer.cancel,
            on_note=lambda note, vel, on, _instrument=None: self.log.append((round(self.timer.now, 3), note, vel, on)),
            on_finish=self._finish,
            clock=self.timer.clock,
        )
        self.rec = record((60, 100, 0.0, 0.5), (64, 80, 0.25, 0.5))

    def _finish(self):
        self.finished += 1

    def test_plays_events_at_their_times(self):
        self.player.play(self.rec, "dal")
        self.assertTrue(self.player.is_playing)
        self.assertEqual(self.player.record_name, "dal")
        self.timer.advance(2)
        self.assertEqual(self.log, [
            (0.0, 60, 100, True),
            (0.25, 64, 80, True),
            (0.5, 60, 0, False),
            (0.75, 64, 0, False),
        ])
        self.assertFalse(self.player.is_playing)
        self.assertEqual(self.finished, 1)
        self.assertEqual(self.player.duration, 0.75)

    def test_late_timer_catches_up_without_losing_events(self):
        self.player.play(self.rec)
        self.timer.jobs = {j: (t + 0.6, cb) for j, (t, cb) in self.timer.jobs.items()}  # késő időzítő
        self.timer.advance(2)
        self.assertEqual([(n, on) for _, n, _, on in self.log], [(60, True), (64, True), (60, False), (64, False)])

    def test_stop_releases_sounding_notes_and_cancels(self):
        self.player.play(self.rec)
        self.timer.advance(0.3)
        self.player.stop()
        self.assertEqual(self.log[-2:], [(0.3, 60, 0, False), (0.3, 64, 0, False)])
        self.assertEqual(self.player.sounding, set())
        self.assertFalse(self.player.is_playing)
        count = len(self.log)
        self.timer.advance(2)
        self.assertEqual(len(self.log), count)
        self.assertEqual(self.finished, 0)

    def test_play_again_replaces_previous(self):
        self.player.play(self.rec)
        self.timer.advance(0.3)
        self.player.play(record((72, 90, 0.0, 0.1)))
        self.timer.advance(1)
        ons = [n for _, n, _, on in self.log if on]
        offs = [n for _, n, _, on in self.log if not on]
        self.assertEqual(ons, [60, 64, 72])
        self.assertCountEqual(offs, [60, 64, 72])
        self.assertEqual(self.finished, 1)

    def test_empty_record_finishes_immediately(self):
        self.player.play(record())
        self.assertFalse(self.player.is_playing)
        self.assertEqual(self.finished, 1)
        self.assertEqual(self.log, [])


class TransportTests(unittest.TestCase):
    """Szünet, ugrás, sebesség és leállítás."""

    def setUp(self):
        self.timer = FakeTimer()
        self.log = []
        self.finished = 0
        self.player = Player(
            after=self.timer.after,
            cancel=self.timer.cancel,
            on_note=lambda note, vel, on, _instrument=None: self.log.append((round(self.timer.now, 3), note, on)),
            on_finish=self._finish,
            clock=self.timer.clock,
        )
        # C4 0.0-1.0, E4 0.5-1.5, G4 2.0-2.5
        self.rec = record((60, 100, 0.0, 1.0), (64, 90, 0.5, 1.0), (67, 80, 2.0, 0.5))

    def _finish(self):
        self.finished += 1

    def test_pause_silences_and_keeps_position(self):
        self.player.play(self.rec)
        self.timer.advance(0.75)
        self.player.pause()
        self.assertTrue(self.player.is_paused)
        self.assertAlmostEqual(self.player.position(), 0.75)
        self.assertEqual(self.player.sounding, set())
        self.assertEqual(self.log[-2:], [(0.75, 60, False), (0.75, 64, False)])
        count = len(self.log)
        self.timer.advance(5)
        self.assertEqual(len(self.log), count)
        self.assertAlmostEqual(self.player.position(), 0.75)

    def test_resume_restarts_sounding_notes_and_continues(self):
        self.player.play(self.rec)
        self.timer.advance(0.75)
        self.player.pause()
        self.timer.advance(3)
        self.log.clear()
        self.player.play_pause()
        self.assertTrue(self.player.is_playing)
        self.assertEqual(self.log, [(3.75, 60, True), (3.75, 64, True)])
        self.timer.advance(2)
        self.assertEqual([(n, on) for _, n, on in self.log[2:]], [(60, False), (64, False), (67, True), (67, False)])
        self.assertEqual(self.log[-1][0], 5.5)  # 0.75 + 1.75 hátralévő idő
        self.assertEqual(self.finished, 1)

    def test_seek_while_playing_into_held_note(self):
        self.player.play(self.rec)
        self.timer.advance(0.1)
        self.log.clear()
        self.player.seek(1.2)
        self.assertEqual(self.log, [(0.1, 60, False), (0.1, 64, True)])
        self.assertEqual(self.player.sounding, {64})
        self.assertAlmostEqual(self.player.position(), 1.2)
        self.timer.advance(2)
        self.assertEqual(self.player.sounding, set())
        self.assertEqual(self.finished, 1)

    def test_seek_while_paused_or_stopped_does_not_sound(self):
        self.player.load(self.rec, "dal")
        self.player.seek(2.1)
        self.assertTrue(self.player.is_paused)
        self.assertEqual(self.log, [])
        self.assertAlmostEqual(self.player.position(), 2.1)
        self.player.play_pause()
        self.assertEqual(self.log, [(0.0, 67, True)])

    def test_seek_is_clamped(self):
        self.player.load(self.rec)
        self.player.seek(-3)
        self.assertEqual(self.player.position(), 0.0)
        self.player.seek(99)
        self.assertEqual(self.player.position(), self.player.duration)

    def test_speed_change_keeps_position_and_changes_tempo(self):
        self.player.play(self.rec)
        self.timer.advance(0.5)
        self.player.set_speed(2.0)
        self.assertAlmostEqual(self.player.position(), 0.5)
        self.timer.advance(0.25)
        self.assertAlmostEqual(self.player.position(), 1.0)
        self.timer.advance(1)
        self.assertEqual(self.finished, 1)
        self.assertEqual(self.log[-1], (1.5, 67, False))  # 0.5 + (2.5 - 0.5) / 2

    def test_slow_speed(self):
        self.player.set_speed(0.5)
        self.player.play(record((60, 100, 0.0, 1.0)))
        self.timer.advance(1.9)
        self.assertEqual(self.player.sounding, {60})
        self.timer.advance(0.2)
        self.assertEqual(self.player.sounding, set())

    def test_invalid_speed(self):
        with self.assertRaises(ValueError):
            self.player.set_speed(0)

    def test_stop_rewinds_but_keeps_record_loaded(self):
        self.player.play(self.rec, "dal")
        self.timer.advance(0.75)
        self.player.stop()
        self.assertEqual(self.player.position(), 0.0)
        self.assertTrue(self.player.is_loaded)
        self.assertEqual(self.player.sounding, set())
        self.log.clear()
        self.player.play_pause()
        self.assertEqual(self.log, [(0.75, 60, True)])

    def test_play_after_end_restarts_from_beginning(self):
        self.player.play(self.rec)
        self.timer.advance(3)
        self.assertEqual(self.finished, 1)
        self.assertAlmostEqual(self.player.position(), self.player.duration)
        self.log.clear()
        self.player.play_pause()
        self.assertEqual(self.log, [(3.0, 60, True)])

    def test_controls_without_record_are_harmless(self):
        self.player.play_pause()
        self.player.pause()
        self.player.seek(1)
        self.player.set_speed(1.5)
        self.player.stop()
        self.assertFalse(self.player.is_loaded)
        self.assertEqual(self.log, [])


FLUTE = {"name": "flute", "program": 73}
PIANO = {"name": "acoustic_grand_piano", "program": 0}


def record_v2(*notes):
    """2. verziójú felvétel: (hang, hangerő, kezdet, hossz, hangszer)."""
    return {
        "format": "synth-mido-record", "version": 2, "created": "2026-10-22T10:00:00",
        "instrument": dict(PIANO), "duration": max((s + d for _, _, s, d, _ in notes), default=0.0),
        "notes": [{"note": n, "velocity": v, "start": s, "duration": d, "instrument": i} for n, v, s, d, i in notes],
    }


class MultiInstrumentTests(unittest.TestCase):
    def test_channels_skip_user_and_drum_channel(self):
        instruments = [{"name": f"i{p}", "program": p} for p in range(16)]
        channels = playback.assign_channels(instruments)
        self.assertEqual(channels[0], 1)
        self.assertNotIn(0, channels.values())
        self.assertNotIn(playback.DRUM_CHANNEL, channels.values())
        self.assertEqual(len(set(list(channels.values())[:14])), 14)  # 14 hangszerig mind külön csatorna
        self.assertEqual(playback.assign_channels([FLUTE, FLUTE]), {73: 1})

    def test_v1_events_have_no_instrument(self):
        self.assertIsNone(build_schedule(record((60, 90, 0.0, 0.5)))[0].instrument)

    def test_v2_events_carry_each_notes_instrument(self):
        events = build_schedule(record_v2((60, 90, 0.0, 0.5, FLUTE), (64, 80, 0.0, 0.5, PIANO)))
        self.assertEqual([(e.on, e.note, e.instrument["name"]) for e in events], [
            (True, 60, "flute"), (True, 64, "acoustic_grand_piano"),
            (False, 60, "flute"), (False, 64, "acoustic_grand_piano"),
        ])

    def test_same_pitch_on_two_instruments_is_not_cut(self):
        events = build_schedule(record_v2((60, 90, 0.0, 1.0, FLUTE), (60, 80, 0.5, 1.0, PIANO)))
        self.assertEqual(
            [(e.time, e.on, e.instrument["program"]) for e in events],
            [(0.0, True, 73), (0.5, True, 0), (1.0, False, 73), (1.5, False, 0)],
        )

    def test_player_reports_instruments_and_releases_every_voice(self):
        timer = FakeTimer()
        log = []
        player = Player(timer.after, timer.cancel, lambda n, v, on, inst: log.append((n, on, inst["name"])),
                        clock=timer.clock)
        player.play(record_v2((60, 90, 0.0, 1.0, FLUTE), (60, 80, 0.0, 1.0, PIANO)), "ket hangszer")
        self.assertEqual(sorted(player.sounding_voices()), [(60, 80, PIANO), (60, 90, FLUTE)])
        self.assertEqual(player.sounding, {60})
        player.stop()
        self.assertEqual(sorted(log), sorted([
            (60, True, "flute"), (60, True, "acoustic_grand_piano"),
            (60, False, "flute"), (60, False, "acoustic_grand_piano"),
        ]))
        self.assertEqual(player.sounding_voices(), [])


if __name__ == "__main__":
    unittest.main()
