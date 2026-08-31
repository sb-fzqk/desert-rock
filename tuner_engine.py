import threading
import sounddevice as sd
import numpy as np
import aubio
from pitch_utilities import TuningStrategyFactory

class TunerEngine:
    MIN_CONFIDENCE = 0.65
    MIN_FREQ = 40.0

    def __init__(self, rate=44100, chunk=2048, sample_format="int16", channels=1, default_preset="E Standard"):
        self.rate = rate
        self.chunk = chunk
        self.format = sample_format
        self.channels = channels

        # Aubio setup for YIN
        self.pitch_o = aubio.pitch("yin", self.chunk, self.chunk, self.rate)
        self.pitch_o.set_unit("Hz")
        self.pitch_o.set_tolerance(0.8)

        # Threading stuff
        self._stop_event = threading.Event()
        self._thread = None

        self._observers = []

        self.current_strategy = TuningStrategyFactory.create_strategy(default_preset)

    @property
    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    def get_current_preset_name(self):
        return self.current_strategy.name

    # Observer handling
    def register_observer(self, fn):
        if fn not in self._observers:
            self._observers.append(fn)

    def remove_observer(self, fn):
        if fn in self._observers:
            self._observers.remove(fn)

    def _notify_observers(self, note, target_freq, cents, detected_freq):
        for fn in self._observers:
            fn(note, target_freq, cents, detected_freq)

    # Threading
    def start(self):
        if not self.is_running:
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._audio_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def close(self):
        self.stop()

    def set_preset(self, preset_name):
        self.current_strategy = TuningStrategyFactory.create_strategy(preset_name)

    # Audio engine thread loop
    def _audio_loop(self):
        stream = sd.RawInputStream(
            samplerate=self.rate,
            blocksize=self.chunk,
            channels=self.channels,
            dtype=self.format
        )
        stream.start()

        try:
            while not self._stop_event.is_set():
                raw_input, overflowed = stream.read(self.chunk)
                audio_data = np.frombuffer(bytes(raw_input), dtype=np.int16).astype(np.float32) / 32768.0

                detected_freq = float(self.pitch_o(audio_data)[0])
                confidence = float(self.pitch_o.get_confidence())

                if confidence > self.MIN_CONFIDENCE and detected_freq > self.MIN_FREQ:
                    note, target_freq, cents = self.current_strategy.get_target(detected_freq)
                    self._notify_observers(note, target_freq, cents, detected_freq)

        finally:
            stream.stop()
            stream.close()