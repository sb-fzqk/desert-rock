import threading
import pyaudio as pa
import numpy as np
import aubio
from pitch_utilities import TuningStrategyFactory

class TunerEngine:
    # Constructor
    def __init__(self, rate=44100, chunk=2048, sample_format=pa.paInt16, channels=1, default_preset="E Standard"):
        # Audio capture constants
        self.rate = rate
        self.chunk = chunk
        self.format = sample_format
        self.channels = channels

        # Aubio setup for YIN
        self.pitch_o = aubio.pitch("yin", self.chunk, self.chunk, self.rate)
        self.pitch_o.set_unit("Hz")
        self.pitch_o.set_tolerance(0.8)

        # Threading stuff
        self.is_running = False
        self._thread = None

        # Obeservers list
        self._observers = []

        # Tuning strategy default
        self.current_strategy = TuningStrategyFactory.create_strategy(default_preset)

    # Getter
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
            self.is_running = True
            self._thread = threading.Thread(target=self._audio_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.is_running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    # Strategy tuning preset
    def set_preset(self, preset_name):
        self.current_strategy = TuningStrategyFactory.create_strategy(preset_name)

    # Audio engine thread loop
    def _audio_loop(self):
        p = pa.PyAudio()

        stream = p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )

        print("Go on, pluck a string, don't be afraid.")

        try:
            while self.is_running:
                raw_input = stream.read(self.chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(raw_input, dtype=np.int16).astype(np.float32) / 32768.0

                detected_freq = float(self.pitch_o(audio_data)[0])
                confidence = float(self.pitch_o.get_confidence())

                if confidence > 0.65 and detected_freq > 40:
                    note, target_freq, cents = self.current_strategy.get_target(detected_freq)
                    self._notify_observers(note, target_freq, cents, detected_freq)

        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()