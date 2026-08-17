import threading
import time
import numpy as np
import pyaudio as pa

class MetronomeEngine:
    def __init__(self, bpm=120, bpme=4, rate=44100, sample_format=pa.paInt16, channels=1):
        self.bpm = bpm
        self.bpme = bpme
        self.rate = rate
        self.format = sample_format
        self.channels = channels

        # Threading stuff
        self.is_running = False
        self._thread = None

        # Current beat variable
        self.current_beat = 0

        # Observers list
        self._observers = []

        # Pre-synthesise the clicks to cache them
        self.click = self._generate_click_buffer(freq=800, duration_ms=15)
        self.higher_click = self._generate_click_buffer(freq=1200, duration_ms=20)

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

    def set_bpme(self, beats):
        self.bpme = max(1, min(12, beats))
        if self.current_beat >= self.bpme:
            self.current_beat = 0

    # Threading
    def start(self):
        if not self.is_running:
            self.is_running = True
            self.current_beat = 0
            self._thread = threading.Thread(target=self._metro_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    # Metronome timing loop (LLM-assisted)
    def _metro_loop(self):
        p = pa.PyAudio()

        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            output=True
        )

        try:
            next_beat_time = time.perf_counter()

            while self.is_running:
                now = time.perf_counter()

                if now >= next_beat_time:
                    # Determine whether higher beat (first) or normal
                    is_higher = (self.current_beat == 0)
                    click_sound = self.higher_click if is_higher else self.click

                    stream.write(click_sound)
                    self._notify_observers(self.current_beat + 1, is_higher)

                    self.current_beat = (self.current_beat + 1) % self.bpme

                    # Schedule next beat
                    beat_interval = 60.0 / self.bpm
                    next_beat_time += beat_interval

                time.sleep(0.0005)

        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()