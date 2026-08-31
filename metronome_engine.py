import threading
import time
import numpy as np
import sounddevice as sd

class MetronomeEngine:
    def __init__(self, bpm=120, ts=4, rate=44100, sample_format="int16", channels=1):
        self.bpm = bpm
        self.ts = ts
        self.rate = rate
        self.format = sample_format
        self.channels = channels

        # Threading stuff
        self._stop_event = threading.Event()
        self._thread = None

        self.current_beat = 0
        
        self._observers = []

        # Pre-synthesise the clicks to cache them
        self.click = self._generate_click_buffer(freq=800, duration_ms=15)
        self.higher_click = self._generate_click_buffer(freq=1200, duration_ms=20)

    @property
    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    # Synthesise a short sine wave click with a rapid decay envelope (LLM-generated)
    def _generate_click_buffer(self, freq, duration_ms):
        num_samples = int(self.rate * (duration_ms / 1000.0))
        t = np.linspace(0, duration_ms / 1000.0, num_samples, False)
        envelope = np.linspace(1.0, 0.0, num_samples)
        audio = np.sin(2 * np.pi * freq * t) * envelope * 0.5

        pcm_data = (audio * 32767).astype(np.int16)

        return pcm_data.tobytes()

    # Observer handling
    def register_observer(self, fn):
        if fn not in self._observers:
            self._observers.append(fn)

    def remove_observer(self, fn):
        if fn in self._observers:
            self._observers.remove(fn)

    def _notify_observers(self, beat_num, is_higher):
        for fn in self._observers:
            fn(beat_num, is_higher)

    # Engine control
    def set_bpm(self, beats):
        self.bpm = max(20, min(400, beats))

    def set_ts(self, beats):
        self.ts = max(1, min(12, beats))
        if self.current_beat >= self.ts:
            self.current_beat = 0

    # Threading
    def start(self):
        if not self.is_running:
            self._stop_event.clear()
            self.current_beat = 0
            self._thread = threading.Thread(target=self._metro_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def close(self):
        self.stop()

    # Metronome timing loop (LLM-assisted)
    def _metro_loop(self):
        stream = sd.RawOutputStream(
            samplerate=self.rate,
            channels=self.channels,
            dtype=self.format
        )
        stream.start()

        try:
            next_beat_time = time.perf_counter()

            while not self._stop_event.is_set():
                now = time.perf_counter()

                if now >= next_beat_time:
                    # Determine whether higher beat (first) or normal
                    is_higher = (self.current_beat == 0)
                    click_sound = self.higher_click if is_higher else self.click

                    stream.write(click_sound)
                    self._notify_observers(self.current_beat + 1, is_higher)

                    self.current_beat = (self.current_beat + 1) % self.ts

                    # Schedule next beat
                    beat_interval = 60.0 / self.bpm
                    next_beat_time += beat_interval

                time.sleep(0.0005)

        finally:
            stream.stop()
            stream.close()