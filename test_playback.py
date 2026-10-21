"""Tesztek a playback modulhoz: ütemezés, alapértelmezett hangszer, lejátszó.

Tk, MIDI és hangeszköz nélkül futnak (az óra és az időzítő hamisított).
Futtatás:  python -m unittest test_playback -v
"""

import unittest

import playback
from playback import Event, Player, build_schedule, default_instrument

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


class FakeTimer:
    """Kézzel léptetett óra + after/cancel."""

    def __init__(self):
        self.now = 0.0
        self.jobs = {}
        self.next_id = 0

    def clock(self):
        return self.now

    def after(self, ms, callback):
        self.next_id += 1
        self.jobs[self.next_id] = (self.now + ms / 1000, callback)
        return self.next_id

    def cancel(self, job):
        self.jobs.pop(job, None)

    def advance(self, seconds):
        """Az idő léptetése; az esedékes időzítők lefutnak (akár késve is, mint a valóságban)."""
        target = self.now + seconds
        while True:
            due = [(t, j) for j, (t, _) in self.jobs.items() if t <= target]
            if not due:
                break
            t, job = min(due)
            self.now = max(self.now, t)
            _, callback = self.jobs.pop(job)
            callback()
        self.now = target


class PlayerTests(unittest.TestCase):
    def setUp(self):
        self.timer = FakeTimer()
        self.log = []
        self.finished = 0
        self.player = Player(
            after=self.timer.after,
            cancel=self.timer.cancel,
            on_note=lambda note, vel, on: self.log.append((round(self.timer.now, 3), note, vel, on)),
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


if __name__ == "__main__":
    unittest.main()
