import threading
import pyaudio as pa
import numpy as np
import scipy.fft as fft
import aubio
from pitch_utilities import hz_to_note, find_nearest_string

class TunerEngine:
    # Constructor
    def __init__(self, rate=44100, chunk=4096, sample_format=pa.paInt16, channels=1):
        self.rate = rate
        self.chunk = chunk
        self.format = sample_format
        self.channels = channels
        self.bin_size = self.rate / self.chunk

        self.pitch_o = aubio.pitch("yin", self.chunk, self.chunk, self.rate)
        self.pitch_o.set_unit("Hz")
        self.pitch_o.set_tolerance(0.8)

        self.is_running = False
        self._thread = None

        self._observers = []

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

    # DSP helper function (LLM generated)
    def _get_interpolated_peak(self, fft_array, max_index):
        if max_index == 0 or max_index >= len(fft_array) - 1:
            return max_index * self.bin_size
        
        alpha = fft_array[max_index - 1]
        beta = fft_array[max_index]
        gamma = fft_array[max_index + 1]

        denominator = alpha - 2 * beta + gamma
        if denominator == 0:
            return max_index * self.bin_size
        
        p = 0.5 * (alpha - gamma) / denominator

        return (max_index + p) * self.bin_size

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

        freqs = fft.fftfreq(self.chunk, 1 / self.rate)
        freq_history = []

        print("Go on, pluck a string, don't be afraid.")

        try:
            while self.is_running:
                raw_input = stream.read(self.chunk, exception_on_overflow=False)
                audio_data = np.frombuffer(raw_input, dtype=np.int16).astype(np.float32) / 32768.0

                detected_freq = float(self.pitch_o(audio_data)[0])
                confidence = float(self.pitch_o.get_confidence())

                if confidence > 0.85 and detected_freq > 40:
                    freq_history.append(detected_freq)
                    if len(freq_history) > 3:
                        freq_history.pop(0)

                    smoothed_freq = sum(freq_history) / len(freq_history)
                    note, target_freq, cents = hz_to_note(smoothed_freq)
                    self._notify_observers(note, target_freq, cents, smoothed_freq)

        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()