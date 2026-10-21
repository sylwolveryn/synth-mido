"""Közös teszt segédek: hamis időzítő / óra és hamis MIDI port / hanggenerátor."""

from synth_mido.audio.tone_synth import ToneSynth


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


class FakePort:
    def __init__(self, name):
        self.name = name
        self.sent = []
        self.closed = False

    def send(self, message):
        self.sent.append(message)

    def close(self):
        self.closed = True


class FakeTone(FakePort):
    def __init__(self):
        super().__init__(ToneSynth.name)
