"""Tesztek a NoteBus-hoz (Observer).

Futtatás:  python -m unittest tests.test_events -v
"""

import unittest

from synth_mido.core import events


class NoteBusTests(unittest.TestCase):
    def test_publish_reaches_all_listeners_in_order(self):
        bus, got = events.NoteBus(), []
        bus.subscribe(lambda e: got.append(("a", e)))
        bus.subscribe(lambda e: got.append(("b", e)))
        event = bus.publish(60, True, 90, events.PLAYBACK)
        self.assertEqual(event, events.NoteEvent(60, True, 90, events.PLAYBACK))
        self.assertEqual(got, [("a", event), ("b", event)])

    def test_defaults(self):
        e = events.NoteBus().publish(64, False)
        self.assertEqual((e.velocity, e.source), (100, events.USER))

    def test_unsubscribe(self):
        bus, got = events.NoteBus(), []
        unsubscribe = bus.subscribe(got.append)
        unsubscribe()
        unsubscribe()  # kétszer is biztonságos
        bus.publish(60, True)
        self.assertEqual(got, [])
        self.assertEqual(bus.listener_count, 0)

    def test_listener_may_unsubscribe_during_publish(self):
        bus, got = events.NoteBus(), []
        holder = {}

        def once(e):
            got.append(e.note)
            holder["off"]()

        holder["off"] = bus.subscribe(once)
        bus.subscribe(lambda e: got.append(-e.note))
        bus.publish(60, True)
        bus.publish(62, True)
        self.assertEqual(got, [60, -60, -62])


if __name__ == "__main__":
    unittest.main()
